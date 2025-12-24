import argparse
import client
import math
from tqdm import tqdm
import utils
from typing import List, Optional
import structlog


DATA_COLLECTION_RETRIES = 10


def convert_measurement_coordinate(
    theta: float, phi: float, radius: float
) -> utils.SphericalCoordinate:
    return utils.SphericalCoordinate(
        (180 - theta) * math.pi / 180,
        (180 - phi) * math.pi / 180,
        radius,
    )


def fetch_measurement(
    logger: structlog.BoundLogger,
    rpi: client.Client,
    theta: float,
    phi: float,
    retries: int = DATA_COLLECTION_RETRIES,
) -> Optional[utils.Measurement]:
    for attempt in range(retries):
        try:
            measurement = rpi.request_measurement(theta, phi)
            return measurement

        except client.InvalidMeasurementChecksumException:
            logger.warn(
                "collected data failed checksum verification",
                theta=theta,
                phi=phi,
                attempt=attempt,
                retries=retries,
            )
            pass

        except client.SignalTooWeakException:
            logger.warn(
                "collected data signal was too weak",
                phi=phi,
                theta=theta,
                attempt=attempt,
                retries=retries,
            )
            pass

    else:
        logger.warn(
            "exceeded max retries; skipping data point",
            phi=phi,
            theta=theta,
            retries=retries,
        )
        return None


def collect_measurements(
    logger: structlog.BoundLogger,
    rpi: client.Client,
    min_theta: int = 90,
    max_theta: int = 160,
    theta_step: int = 5,
    min_phi: int = 0,
    max_phi: int = 160,
    phi_step: int = 5,
) -> List[utils.SphericalCoordinate]:
    theta_steps = (max_theta - min_theta) // theta_step + 1
    phi_steps = (max_phi - min_phi) // phi_step + 1
    total_steps = theta_steps * phi_steps
    strengths = []
    coordinates: List[utils.SphericalCoordinate] = []
    with tqdm(total=total_steps) as progress:
        progress.set_description("Collecting measurements")

        for theta in range(min_theta, max_theta + 1, theta_step):
            for phi in range(min_phi, max_phi + 1, phi_step):
                if (theta // theta_step) % 2 != 0:
                    phi = max_phi - phi

                measurement = fetch_measurement(logger, rpi, theta, phi)
                strength = measurement.strength if measurement else math.nan
                strengths.append(strength)
                coordinate = convert_measurement_coordinate(
                    theta,
                    phi,
                    measurement.distance if measurement else math.nan,
                )
                coordinates.append(coordinate)

                if measurement is not None:
                    progress.set_postfix(temperature=measurement.temperature)

                progress.update(1)

    return coordinates, strengths


def store_output(filename: str, output: List[utils.SphericalCoordinate], strengths):
    lines = ["theta,phi,radius, strengths\n"]
    count = 0
    for coordinate in output:
        lines.append(
            f"{coordinate.theta},{coordinate.phi},{coordinate.radius},{strengths[count]}\n"
        )
        count += 1

    with open(filename, "w+") as f:
        f.write("".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="RaspberryPaul",
        description="Paul's TM",
    )

    parser.add_argument("-H", "--host", type=str, required=True)
    parser.add_argument("-p", "--port", type=int, required=True)
    parser.add_argument("-o", "--output", type=str, required=True)
    args = parser.parse_args()

    logger = structlog.get_logger()

    rpi = client.NetworkedClient(args.host, int(args.port))
    coordstrength = collect_measurements(logger, rpi)
    coordinates = coordstrength[0]
    strengths = coordstrength[1]
    rpi.close()

    store_output(args.output, coordinates, strengths)
