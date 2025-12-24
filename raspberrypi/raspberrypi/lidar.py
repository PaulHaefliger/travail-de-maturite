import serial
import utils
from typing import List


MIN_STRENGTH = 200


class SignalTooWeakException(Exception):
    pass


class InvalidMeasurementChecksumException(Exception):
    pass


class Lidar:
    def measure(self) -> utils.Measurement:
        raise Exception("not implemented")


def convert_distance(low: bytes, high: bytes) -> float:
    return (ord(high) * 256) + ord(low)


def convert_strength(low: bytes, high: bytes) -> float:
    return (ord(high) * 256) + ord(low)


def convert_temperature(low: bytes, high: bytes) -> float:
    return ((ord(high) * 256) + (ord(low))) / 8 - 256


def compute_checksum(frame: List[bytes]) -> int:
    checksum = hex(sum([ord(i) for i in frame[:-1]]))[-2:]
    return int(f"0x{checksum}", 16)


def verify_checksum(frame: List[bytes]) -> bool:
    return compute_checksum(frame) == ord(frame[-1])


class LidarController(Lidar):
    def __init__(self, serial_port: str = "/dev/ttyUSB0"):
        self.lidar = serial.Serial(serial_port, 115200, timeout=1)

    def __clear(self):
        self.lidar.reset_input_buffer()
        self.lidar.reset_output_buffer()

    def __read(self) -> bytes:
        return self.lidar.read()

    def __read_until(self, until: bytes) -> bytes:
        return self.lidar.read_until(until)

    def measure(self) -> utils.Measurement:
        self.__clear()
        _ = self.__read_until(b"YY")

        frame = [b"Y", b"Y"]
        for _ in range(7):
            frame.append(self.__read())

        if not verify_checksum(frame):
            raise InvalidMeasurementChecksumException()

        distance = convert_distance(frame[2], frame[3])

        strength = convert_strength(frame[4], frame[5])
        if strength < MIN_STRENGTH:
            raise SignalTooWeakException()

        temperature = convert_temperature(frame[6], frame[7])

        return utils.Measurement(distance, strength, temperature)
