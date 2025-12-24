import socket
import structlog
import json
import datacollector
import lidar


def get_ip_address() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]


class Server:
    def __init__(
        self, logger: structlog.BoundLogger, data_collector: datacollector.DataCollector
    ):
        self.logger = logger
        self.data_collector = data_collector

    def __handle_connection(self, conn: socket.socket):
        while True:
            data = conn.recv(1024)
            if not data:
                break

            request = json.loads(data)
            phi: int = request["phi"]
            theta: int = request["theta"]
            self.logger.info("received request", phi=phi, theta=theta)

            try:
                measurement = self.data_collector.collect_measurement(
                    theta,
                    phi,
                )
                self.logger.info(
                    "collected measurement",
                    phi=phi,
                    theta=theta,
                    distance=measurement.distance,
                    strength=measurement.strength,
                    temperature=measurement.temperature,
                )

                response = json.dumps(
                    {
                        "distance": measurement.distance,
                        "strength": measurement.strength,
                        "temperature": measurement.temperature,
                    }
                )
                conn.send(bytes(response, "utf-8"))

            except lidar.InvalidMeasurementChecksumException:
                self.logger.warn(
                    "collected data failed checksum verification",
                    phi=phi,
                    theta=theta,
                )
                response = json.dumps({"error_code": 1})
                conn.send(bytes(response, "utf-8"))

            except lidar.SignalTooWeakException:
                self.logger.warn(
                    "collected data signal was too weak",
                    phi=phi,
                    theta=theta,
                )
                response = json.dumps({"error_code": 2})
                conn.send(bytes(response, "utf-8"))

    def __listen(self, sock: socket.socket):
        while True:
            self.logger.info("waiting for connection")

            conn, address = sock.accept()
            self.logger.info("client connected", ip=address[0])

            with conn:
                self.__handle_connection(conn)

            self.logger.info("client disconnected", ip=address[0])

    def serve(self, port: int):
        host = get_ip_address()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self.logger.info("starting server", host=host, port=port)
            sock.bind((host, port))

            self.logger.info("listening for connections", host=host, port=port)
            sock.listen()
            self.__listen(sock)
