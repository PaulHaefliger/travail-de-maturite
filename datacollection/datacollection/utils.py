from dataclasses import dataclass


@dataclass
class SphericalCoordinate:
    theta: float
    phi: float
    radius: float


@dataclass
class Measurement:
    distance: float
    strength: float
    temperature: float
