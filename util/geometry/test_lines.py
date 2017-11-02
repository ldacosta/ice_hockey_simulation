import unittest

from random import random, sample, randint

from util.geometry.lines import StraightLine

class TestStraightLines(unittest.TestCase):
    """Testing definitions of a player."""

    def setUp(self):
        """Initialization"""
        pass

    def test_goes_by(self):
        min_x = randint(-100, 100)
        max_x = min_x + randint(1, 100)
        a_y = randint(-100, 100)
        another_y = randint(-100, 100)
        sl = StraightLine.goes_by(point_1=(min_x, a_y), point_2=(max_x, another_y))
        self.assertAlmostEqual(sl.apply_to(an_x=min_x), a_y)
        self.assertAlmostEqual(sl.apply_to(an_x=max_x), another_y)

