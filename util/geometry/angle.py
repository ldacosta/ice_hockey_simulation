import abc
import math
import random
from util.base import normalize_to

class Angle(metaclass=abc.ABCMeta):

    def __init__(self, value: float, sinus: float, cosinus: float):
        self.value = value
        self.sin = sinus
        self.cos = cosinus

class AngleInRadians(Angle):


    DIGITS_FOR_CMP = 4
    PI_HALF = math.pi / 2
    THREE_HALFS_OF_PI = 3 * math.pi / 2

    def __init__(self, value: float):
        """
        Initializes an angle in radians
        :param value: the positive value of this angle (ie, between 0 and 2*Pi)
        """
        value = AngleInRadians.normalize(value)
        assert (value >= 0) and (value <= 2 * math.pi) # sanity check
        super().__init__(value, sinus=math.sin(value), cosinus=math.cos(value))

    @classmethod
    def from_degrees(cls, angle_in_degrees):
        return cls(math.radians(angle_in_degrees.value))

    @classmethod
    def from_minus_pi_to_plus_pi(cls, value: float):
        assert (value >= -math.pi) and (value <= math.pi)
        if value >= 0:
            return cls(value=value)
        else:
            return cls(value=2 * math.pi + value)

    @classmethod
    def random(cls):
        """Creates a randomly chosen angle."""
        an_instance = cls(value=0.0)
        an_instance.randomly_mutate()
        return an_instance

    @classmethod
    def normalize(cls, a_value: float) -> float:
        """Brings value to [0, 2*Pi]"""
        abs_value = abs(a_value)
        abs_value_norm = abs_value % (2 * math.pi)
        if a_value < 0:
            return 2 * math.pi - abs_value_norm
        else:
            return abs_value_norm

    def __iadd__(self, other):
        other_as_angle = AngleInRadians.create_from(other)
        self.value = AngleInRadians.normalize(self.value + other_as_angle.value)
        return self

    @classmethod
    def create_from(cls, other):
        if isinstance(other, AngleInRadians):
            other_as_angle = other
        elif isinstance(other, float) or isinstance(other, int):
            other_as_angle = AngleInRadians(value=other)
        else:
            raise RuntimeError("I don't know how to add an Angle to something non-numeric")
        return other_as_angle

    def __isub__(self, other):
        other_as_angle = AngleInRadians.create_from(other)
        self.value = AngleInRadians.normalize(self.value - other_as_angle.value)
        return self

    def __lt__(self, other):
        other_as_angle = AngleInRadians.create_from(other)
        return self.value < other_as_angle.value

    def randomly_mutate(self):
        """Changes the value of this angle, at random."""
        self.value = normalize_to(random.random(), new_min=0.0, new_max=2*math.pi, old_min=0.0, old_max=1.0)

    def __str__(self):
        if math.isclose(self.value, AngleInRadians.PI_HALF):
            return "Angle in radians: Pi / 2 (= %.4f)" % (self.value)
        elif math.isclose(self.value, math.pi):
            return "Angle in radians: Pi (= %.4f)" % (self.value)
        elif math.isclose(self.value, AngleInRadians.THREE_HALFS_OF_PI):
            return "Angle in radians: 3*Pi/2 (= %.4f)" % (self.value)
        else:
            return "Angle in radians = %.3f (Pi/2: %.3f, Pi:%.3f, 3/2*Pi:%.3f)" % (self.value, math.pi/2, math.pi, 3*math.pi/2)

class AngleInDegrees(Angle):

    def __init__(self, value: float):
        assert (value >= 0) and (value <= 360)
        super().__init__(value, sinus=math.sin(math.radians(value)), cosinus=math.cos(math.radians(value)))

    @classmethod
    def from_radians(cls, angle_in_radians: AngleInRadians):
        return cls(math.degrees(angle_in_radians.value))

# https://stackoverflow.com/questions/20023209/function-for-rotating-2d-objects
def rotatePoint(centerPoint, point, angle: AngleInRadians):
    """Rotates a point around another centerPoint. Angle is in degrees.
    Rotation is counter-clockwise"""
    angle = math.radians(angle.value)
    temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
    temp_point = ( temp_point[0]*math.cos(angle)-temp_point[1]*math.sin(angle) , temp_point[0]*math.sin(angle)+temp_point[1]*math.cos(angle))
    temp_point = temp_point[0]+centerPoint[0] , temp_point[1]+centerPoint[1]
    return temp_point

if __name__ == "__main__":
    # some_values = [("2 Pi", 2 * math.pi), ("Pi", math.pi), ("10 Pi", 10 * math.pi), ("-Pi", -math.pi), ("-7 Pi", -7 * math.pi)]
    # for (a_label, a_value) in some_values:
    #     print("%s = %.2f, normalized = %.2f" % (a_label, a_value, AngleInRadians.normalize(a_value)))

    a = AngleInRadians(math.pi)
    print(a)
    # a += AngleInRadians(math.pi/2)
    # print(a)
    a -= 2 * math.pi # /2
    print(a)
