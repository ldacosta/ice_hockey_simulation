import unittest

from hockey.core.half_rink import HockeyHalfRink


class TestHalfRink(unittest.TestCase):
    """Testing definitions of a half-ice rink."""

    def test_creation(self):
        """Very simple sanity test."""

        half_ice_rink = HockeyHalfRink(how_many_defense=5, how_many_offense=5)
        print(half_ice_rink)

