

import numpy as np
from typing import Tuple

from geometry.angle import AngleInRadians

class Vector2D(object):
    """Representation of 2D Vector"""

    def __init__(self, pt_from: Tuple[float, float], pt_to: Tuple[float, float]):
        self.tip = np.asarray([pt_to[0] - pt_from[0], pt_to[1] - pt_from[1]])

    @classmethod
    def from_angle(cls, angle_in_radians: AngleInRadians):
        return cls(pt_from=(0.0, 0.0), pt_to=(angle_in_radians.cos, angle_in_radians.sin))

    @classmethod
    def from_tip(cls, tip: Tuple[float, float]):
        return cls(pt_from=(0,0), pt_to=tip)

    def __getitem__(self, item):
        if item > 1:
            raise IndexError("A 2D vector only has 2 dimensions (0 and 1, so %d makes no sense)" % (item))
        return self.tip[item]

    def is_zero(self) -> bool:
        return np.all(self.tip == 0.0)

    def scalar_multiply(self, a_scalar: float):
        self.tip *= a_scalar
        return self

    def norm(self) -> float:
        return np.linalg.norm(self.tip)

    def angle_with_x_axis(self) -> AngleInRadians:
        return np.arctan(self.tip[1] / self.tip[0])

    def __str__(self):
        return "vector2D(%f,%f)" % (self.tip[0], self.tip[1])

X_UNIT_VECTOR = Vector2D(pt_from=(0,0), pt_to=(1,0))
Y_UNIT_VECTOR = Vector2D(pt_from=(0,0), pt_to=(0,1))
NULL_2D_VECTOR = Vector2D(pt_from=(0,0), pt_to=(0,0))



def angle_between(v1: Vector2D ,v2: Vector2D) -> AngleInRadians:
    """Angle (in radians) between 2 vectors."""
    return AngleInRadians.from_minus_pi_to_plus_pi(
        value=np.arcsin(np.cross(v1.tip, v2.tip) / (np.linalg.norm(v1.tip) * np.linalg.norm(v2.tip))))

if __name__ == "__main__":
    v = Vector2D(pt_from = (10,-10), pt_to = (1,1))
    print(v)
