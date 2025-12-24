import matplotlib.pyplot as plt
from typing import List, Tuple
import math
import utils
import structlog
import argparse


def load_output(filename: str) -> List[utils.SphericalCoordinate]:
    with open(filename, "r") as f:
        data = f.read()
        lines = data.split("\n")[1:]

        coordinates: List[utils.SphericalCoordinate] = []
        strength = []
        for line in lines:
            if line != "":
                values = line.split(",")
                coordinates.append(
                    utils.SphericalCoordinate(
                        float(values[0]),
                        float(values[1]),
                        float(values[2]),
                    )
                )
                strength.append(float(values[3]))

        return coordinates, strength


def convert_spherical_to_cartesian(
    coordinate: utils.SphericalCoordinate,
) -> utils.CartesianCoordinate:
    return utils.CartesianCoordinate(
        coordinate.radius * math.sin(coordinate.theta) * math.cos(coordinate.phi),
        coordinate.radius * math.sin(coordinate.theta) * math.sin(coordinate.phi),
        coordinate.radius * math.cos(coordinate.theta),
    )


def calculate_triangles(data: List[utils.SphericalCoordinate]) -> List[List[int]]:
    theta_count = len(set([coordinate.theta for coordinate in data]))
    phi_count = len(set([coordinate.phi for coordinate in data]))
    expected_total_count = theta_count * phi_count
    if expected_total_count != len(data):
        raise Exception(
            f"expected {expected_total_count} data points but got {len(data)}"
        )

    triangles: List[List[int]] = []
    for theta in range(theta_count - 1):
        for phi in range(phi_count - 1):
            triangles.append(
                [
                    (theta * phi_count) + phi,
                    ((theta + 1) * phi_count) + phi,
                    (theta * phi_count) + phi + 1,
                ]
            )
            triangles.append(
                [
                    ((theta + 1) * phi_count) + phi + 1,
                    ((theta + 1) * phi_count) + phi,
                    (theta * phi_count) + phi + 1,
                ]
            )

    return triangles


def calculate_points(
    data: List[utils.SphericalCoordinate],
) -> Tuple[List[utils.CartesianCoordinate], List[List[int]]]:
    triangles = calculate_triangles(data)
    coordinates = [convert_spherical_to_cartesian(coordinate) for coordinate in data]

    return coordinates, triangles


def plot_map(
    x: List[float], y: List[float], z: List[float], triangles: List[List[int]]
):
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    ax.plot_trisurf(x, y, z, triangles=triangles)

    ax.set_xlabel("X(cm)")
    ax.set_ylabel("Y(cm)")
    ax.set_zlabel("Z(cm)")

    plt.show()


def strength_coefficient(x):
    return float((x - mini) / maxi)


def color(x):
    cmap = plt.get_cmap("inferno")
    plt.set_cmap(cmap)
    rgba = cmap(strength_coefficient(x))
    return rgba


def color_list(x):
    for i in x:
        i = color(i)
    return x


def plot_data(data: List[utils.CartesianCoordinate], triangles: List[List[int]]):
    x = [coordinate.x for coordinate in data]
    y = [coordinate.y for coordinate in data]
    z = [coordinate.z for coordinate in data]

    plot_map(x, y, z, triangles)


def scatter_data(data: List[utils.CartesianCoordinate]):
    x = [coordinate.x for coordinate in data]
    y = [coordinate.y for coordinate in data]
    z = [coordinate.z for coordinate in data]
    s = [strength for strength in strength]
    ax = plt.axes(projection="3d")
    ax.scatter3D(x, y, z, s=10, c=color_list(s))
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="RaspberryPaul",
        description="Paul's TM",
    )

    parser.add_argument("-d", "--data", type=str, required=True)
    args = parser.parse_args()

    logger = structlog.get_logger()

    coordinates = load_output(args.data)[0]
    strength = load_output(args.data)[1]
    mini = int(min(strength))
    maxi = int(max(strength))
    points, triangles = calculate_points(coordinates)

    logger.info(
        "plotting data",
        points=len(points),
        missing_points=len(
            [coordinate for coordinate in coordinates if coordinate.radius is math.nan]
        ),
    )

    scatter_data(points)
