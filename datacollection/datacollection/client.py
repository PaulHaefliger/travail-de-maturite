import socket
import json
import utils


class SignalTooWeakException(Exception):
    pass


class InvalidMeasurementChecksumException(Exception):
    pass


class Client:
    def request_measurement(self, theta: int, phi: int) -> utils.Measurement:
        raise Exception("not implemented")

    def close(self):
        raise Exception("not implemented")


class MockClient(Client):
    def request_measurement(self, theta: int, phi: int) -> utils.Measurement:
        return utils.Measurement(10, 10, 10)

    def close(self):
        pass


class NetworkedClient(Client):
    def __init__(self, host: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def request_measurement(self, theta: int, phi: int) -> utils.Measurement:
        angles = {
            "phi": phi,
            "theta": theta,
        }
        request = json.dumps(angles)
        self.socket.send(bytes(request, "utf-8"))

        response = self.socket.recv(1024)
        measurement = json.loads(response)

        if "error_code" in measurement:
            error_code = measurement["error_code"]
            if error_code == 1:
                raise InvalidMeasurementChecksumException()
            elif error_code == 2:
                raise SignalTooWeakException()
            else:
                raise Exception("unknown error")

        return utils.Measurement(
            measurement["distance"],
            measurement["strength"],
            measurement["temperature"],
        )

    def close(self):
        self.socket.close()
