import unittest
from random import sample as randomsample
from xcs.bitstrings import BitString as XCSBitString, BitCondition

from hockey.core.half_rink import HockeyHalfRink
from geometry.angle import AngleInRadians
from hockey.behaviour.core.environment_state import EnvironmentState
from hockey.behaviour.core.bitstring_environment_state import BitstringEnvironmentState, angle_to_bitstring, distance_to_bitstring

class TestBitstringEncoding(unittest.TestCase):
    """Testing definitions of a player."""

    def setUp(self):
        """Initialization"""
        self.NUM_SLICES = 20
        self.half_ice_rink = HockeyHalfRink(how_many_defense=5, how_many_offense=5, one_step_in_seconds=1/20, collect_data_every_secs=1, record_this_many_minutes=1)

    def test_proper_encoding(self):
        """Are things that I want to encode properly defined?"""
        env_state = EnvironmentState(me=self.half_ice_rink.defense[0], puck_pos_opt=None, puck_owner_opt=None)
        bitstring_state = BitstringEnvironmentState(full_state=env_state)
        bitstring_state.build_defs() # if this doesn't blow up, we're good:
        print(BitstringEnvironmentState.explain_condition(
            condition=BitCondition('#0#01#0111#00#00###0#00001#0011#1111#000###0000#0#00#0###0')))
        self.assertTrue(True)

    def test_angle_encoding(self):
        """How is an angle encoded."""
        angles_to_try = list(map(lambda v: v / 100, randomsample(range(0, int(round(AngleInRadians.PI * 100))), 50)))
        angles_to_try.append(0)
        angles_to_try.append(AngleInRadians.PI)
        for agent_can_see_puck in [True, False]:
            for angle_to_test in angles_to_try:
                r = angle_to_bitstring(can_see=agent_can_see_puck,
                                       angle=AngleInRadians(angle_to_test),
                                       num_slices_on_angles=self.NUM_SLICES)
                self.assertEqual(len(r), self.NUM_SLICES + 1)
                # how many bits ON:
                self.assertTrue(r.count() <= 1) # max 1 bit is ON.
                if not agent_can_see_puck:
                    self.assertFalse(r.any()) # no bit is set to 1
                else:
                    self.assertEqual(r.count(), 1)
                # specific bits:
                    if angle_to_test == 0:
                        self.assertEqual(r[0], 1)
                    elif angle_to_test == AngleInRadians.PI:
                        self.assertEqual(r[-1], 1)

    def test_distance_encoding(self):
        """How is a distance encoded."""
        distance_range = [0, 10, 15, 22]
        distances_to_try = randomsample(range(0, max(distance_range) * 2), min(len(distance_range), 50))
        distances_to_try.append(0)
        distances_to_try.append(max(distance_range))
        for agent_can_see_puck in [True, False]:
            for distance_to_test in distances_to_try:
                r = distance_to_bitstring(can_see=agent_can_see_puck,
                                          distance=distance_to_test,
                                          range_distances=distance_range)
                self.assertEqual(len(r), len(distance_range))
                # how many bits ON:
                self.assertTrue(r.count() <= 1) # max 1 bit is ON.
                if not agent_can_see_puck:
                    self.assertFalse(r.any()) # no bit is set to 1
                else:
                    if distance_to_test <= max(distance_range):
                        self.assertEqual(r.count(), 1)
                    else:
                        self.assertEqual(r.count(), 0)
                    # specific bits:
                    if distance_to_test == 0:
                        self.assertEqual(r[0], 1, "result is %s, distance to test is %.2f" % (r, distance_to_test))
                    elif distance_to_test == max(distance_range):
                        self.assertEqual(r[-1], 1, "result is %s, distance to test is %.2f" % (r, distance_to_test))
