import random
from enum import Enum, auto
from typing import Tuple
from geometry.angle import AngleInDegrees

class Directions(Enum):
    EAST = auto()
    WEST = auto()
    NORTH = auto()
    SOUTH = auto()
    NORTH_EAST = auto()
    NORTH_WEST = auto()
    SOUTH_EAST = auto()
    SOUTH_WEST = auto()

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


def get_random_direction() -> Directions:
    return random.choice(list(Directions))

def directions2angle(d: Directions) -> AngleInDegrees:
    if d == Directions.EAST:
        angle = 0
    elif d == Directions.WEST:
        angle = 180
    elif d == Directions.NORTH:
        angle = 90
    elif d == Directions.SOUTH:
        angle = 270
    elif d == Directions.NORTH_EAST:
        angle = 45
    elif d == Directions.NORTH_WEST:
        angle = 135
    elif d == Directions.SOUTH_EAST:
        angle = 315
    elif d == Directions.SOUTH_WEST:
        angle = 225
    else:
        raise RuntimeError("I do not know what direction is %s" % (d))
    return AngleInDegrees(value=angle)

def directions2vector(d: Directions) -> Tuple[float, float]:
    angle = directions2angle(d)
    return (angle.cos, angle.sin)
