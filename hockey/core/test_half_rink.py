import unittest

from geometry.point import Point
from geometry.vector import Vec2d
from geometry.angle import AngleInRadians
from hockey.core.half_rink import HockeyHalfRink


class TestHalfRink(unittest.TestCase):
    """Testing definitions of a half-ice rink."""

    def setUp(self):
        """Initialization"""
        self.half_ice_rink = HockeyHalfRink(how_many_defense=5, how_many_offense=5, one_step_in_seconds=1/20, collect_data_every_secs=1, record_this_many_minutes=1)
        print(self.half_ice_rink)

    def test_random_points(self):
        """Are random points generated inside of the ice?"""
        for _ in range(10):
            a_pt = self.half_ice_rink.get_random_position()
            self.assertGreaterEqual(a_pt.x, 0)
            self.assertGreaterEqual(a_pt.y, 0)
            self.assertLessEqual(a_pt.x, self.half_ice_rink.width)
            self.assertLessEqual(a_pt.y, self.half_ice_rink.height)

    def test_angle_to_puck(self):

        self.half_ice_rink.space.place_agent(self.half_ice_rink.puck, (0,0))
        a = self.half_ice_rink.angle_to_puck(a_pos=Point(97.42, 83.20), looking_at=Vec2d.from_to(Point(0,0), Point(-11.69, 3.97)))
        print(a)
        assert a <= AngleInRadians(AngleInRadians.PI_HALF)
