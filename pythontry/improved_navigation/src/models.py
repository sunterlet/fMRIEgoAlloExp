from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np

@dataclass
class Vector2D:
    x: float
    y: float

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        return np.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self) -> 'Vector2D':
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return self * (1.0 / mag)

    def to_screen_coords(self, center: Tuple[int, int], scale: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        return (
            center[0] + int(self.x * scale),
            center[1] - int(self.y * scale)
        )

@dataclass
class TrialData:
    trial_info: str
    trial_type: str
    exploration_time: float
    annotation_time: float
    encountered_goal: Optional[Vector2D]
    annotation: Vector2D
    error_distance: Optional[float]

@dataclass
class ContinuousData:
    trial_info: str
    phase: str
    time: float
    position: Vector2D 