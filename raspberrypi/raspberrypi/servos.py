import time
import smbus2 as smbus
from typing import Any


BOARD_I2C_BUS = 1


def get_degrees_pulse_duration(degrees: float) -> float:
    return (degrees + 45) / (90 * 1000)


def get_pulse_duration_value(pulse: float, frequency: float) -> float:
    pulse_length = 1000 / frequency / 4096
    return int(pulse * 1000 / pulse_length)


class Servos:
    def rotate_theta(self, angle: float):
        raise Exception("not implemented")

    def rotate_phi(self, angle: float):
        raise Exception("not implemented")


class ServoController(Servos):
    BOARD_I2C_ADDR = 0x40
    CHANNEL_0_START = 0x06
    CHANNEL_0_END = 0x08
    CHANNEL_1_START = 0x0A
    CHANNEL_1_END = 0x0C
    MODE1_REG_ADDR = 0
    PRE_SCALE_REG_ADDR = 0xFE

    @staticmethod
    def __delay(count: int = 1):
        time.sleep(count * 0.25)

    def __write_byte_data(self, address: int, value: Any):
        self.bus.write_byte_data(self.BOARD_I2C_ADDR, address, value)

    def __write_word_data(self, address: int, value: Any):
        self.bus.write_word_data(self.BOARD_I2C_ADDR, address, value)

    def __set_servo_position(self, servo: int, angle: float):
        if angle < 0 or angle > 160:
            raise Exception(
                "invalid servo angle. angle must be between 0 and 180 degrees"
            )

        pulse = get_degrees_pulse_duration(angle)
        value = get_pulse_duration_value(pulse, 50)
        self.__write_word_data(servo, value)
        self.__delay(2)

    def __init__(
        self,
        i2c_bus: int = BOARD_I2C_BUS,
    ):
        self.bus = smbus.SMBus(i2c_bus)

        # Enable prescaler change
        self.__write_byte_data(self.MODE1_REG_ADDR, 0x10)

        # Set prescaler to 50Hz from datasheet calculation
        self.__write_byte_data(self.PRE_SCALE_REG_ADDR, 0x80)
        self.__delay()

        # Enable word writes
        self.__write_byte_data(self.MODE1_REG_ADDR, 0x20)

        # Set channel start times
        self.__write_word_data(self.CHANNEL_0_START, 0)
        self.__write_word_data(self.CHANNEL_1_START, 0)

        # Reset to start position
        self.__set_servo_position(self.CHANNEL_0_END, 0)
        self.__set_servo_position(self.CHANNEL_1_END, 0)

    def rotate_theta(self, angle: float):  # top
        self.__set_servo_position(self.CHANNEL_0_END, angle)

    def rotate_phi(self, angle: float):  # bottom
        self.__set_servo_position(self.CHANNEL_1_END, angle)
