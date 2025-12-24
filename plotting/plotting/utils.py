from dataclasses import dataclass


@dataclass
class CartesianCoordinate:
    x: float
    y: float
    z: float


@dataclass
class SphericalCoordinate:
    theta: float
    phi: float
    radius: float
