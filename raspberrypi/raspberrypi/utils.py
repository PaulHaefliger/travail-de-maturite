from dataclasses import dataclass


@dataclass
class Measurement:
    distance: float
    strength: float
    temperature: float
