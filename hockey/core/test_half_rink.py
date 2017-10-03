import unittest

from hockey.core.half_rink import HockeyHalfRink


class TestHalfRink(unittest.TestCase):
    """Testing definitions of a half-ice rink."""

    def setUp(self):
        """Initialization"""
        self.half_ice_rink = HockeyHalfRink(how_many_defense=5, how_many_offense=5)
        print(self.half_ice_rink)

    def test_random_points(self):
        """Are random points generated inside of the ice?"""
        for _ in range(10):
            a_pt = self.half_ice_rink.get_random_position()
            self.assertGreaterEqual(a_pt.x, 0)
            self.assertGreaterEqual(a_pt.y, 0)
            self.assertLessEqual(a_pt.x, self.half_ice_rink.width)
            self.assertLessEqual(a_pt.y, self.half_ice_rink.height)
