import utils
import lidar
import servos


class DataCollector:
    def collect_measurement(self, theta: int, phi: int) -> utils.Measurement:
        raise Exception("not implemented")


class HardwareDataCollector(DataCollector):
    def __init__(self, servo_controller: servos.Servos, lidar_controller: lidar.Lidar):
        self.servos = servo_controller
        self.lidar = lidar_controller

    def collect_measurement(self, theta: int, phi: int) -> utils.Measurement:
        self.servos.rotate_theta(theta)
        self.servos.rotate_phi(phi)
        measurement = self.lidar.measure()

        return measurement
