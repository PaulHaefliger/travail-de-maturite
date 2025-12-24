import server
import servos
import lidar
import datacollector
import structlog
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="RaspberryPaul",
        description="Paul's TM",
    )

    parser.add_argument("-p", "--port", type=int, required=True)
    args = parser.parse_args()

    logger = structlog.get_logger()

    lidar_controller = lidar.LidarController()
    servo_controller = servos.ServoController()
    data_collector = datacollector.HardwareDataCollector(
        servo_controller,
        lidar_controller,
    )

    lidar_server = server.Server(logger, data_collector)
    lidar_server.serve(int(args.port))
