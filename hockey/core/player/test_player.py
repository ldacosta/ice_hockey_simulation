import unittest
from copy import copy
from random import sample as randomsample

from geometry.vector import Vec2d, X_UNIT_VECTOR, Y_UNIT_VECTOR
from geometry.point import Point
from geometry.angle import AngleInRadians
from hockey.core.half_rink import HockeyHalfRink
from hockey.behaviour.core.action import HockeyAction
from hockey.core.player.base import Player

class TestBasePlayer(unittest.TestCase):
    """Testing definitions of a player."""

    def assert_vectors_almost_equals(self, v1: Vec2d, v2: Vec2d):
        self.assertAlmostEquals(v1.x, v2.x)
        self.assertAlmostEquals(v1.y, v2.y)

    def setUp(self):
        """Initialization"""
        self.half_ice_rink = HockeyHalfRink(how_many_defense=5, how_many_offense=5, one_step_in_seconds=1/20, collect_data_every_secs=1, record_this_many_minutes=1)

    def test_reach_makes_sense(self):
        """Reach...?"""
        for player in self.half_ice_rink.defense + self.half_ice_rink.attack:
            self.assertTrue(player.reach <= player.height)

    def test_looking_at(self):
        """Point in front of players must be well defined."""
        for player in self.half_ice_rink.defense + self.half_ice_rink.attack:
            # looking on X+
            player.angle_looking_at = AngleInRadians(0)
            self.assert_vectors_almost_equals(player.vector_looking_at().normalized(), X_UNIT_VECTOR)
            # looking on Y+
            player.angle_looking_at = AngleInRadians(AngleInRadians.PI_HALF)
            self.assert_vectors_almost_equals(player.vector_looking_at().normalized(), Y_UNIT_VECTOR)
            # looking on X-
            player.angle_looking_at = AngleInRadians(AngleInRadians.PI)
            self.assert_vectors_almost_equals(player.vector_looking_at().normalized(), X_UNIT_VECTOR * -1)
            # looking on Y+
            player.angle_looking_at = AngleInRadians(AngleInRadians.THREE_HALFS_OF_PI)
            self.assert_vectors_almost_equals(player.vector_looking_at().normalized(), Y_UNIT_VECTOR * -1)

    def test_pt_in_front(self):
        """Point in front of players must be well defined."""
        # generic
        for player in self.half_ice_rink.defense + self.half_ice_rink.attack:
            p_in_front = player.__pt_in_front_of_me__()
            v_to_front = Vec2d.from_to(from_pt=player.pos, to_pt=p_in_front)
            # does it have the right size?
            self.assertAlmostEquals(v_to_front.norm(), player.reach)
            v_looking_at = player.vector_looking_at()
            # these vectors must be colineal
            self.assert_vectors_almost_equals(v_to_front.normalized(), v_looking_at.normalized())

    def move_puck_to(self, a_pt: Point):
        self.half_ice_rink.puck.pos.x = a_pt.x
        self.half_ice_rink.puck.pos.y = a_pt.y

    def test_can_see_puck(self):
        """ 'Seeing' the puck works?"""
        for _ in range(10):
            self.half_ice_rink.set_random_positions_for_agents()
            orig_pos = copy(self.half_ice_rink.puck.pos)
            for player in self.half_ice_rink.defense + self.half_ice_rink.attack:
                # (1) player is on the same position as puck
                self.move_puck_to(player.pos)
                self.assertTrue(player.can_see_puck())
                self.move_puck_to(orig_pos)
                # (2) puck right in front!
                self.move_puck_to(player.__pt_in_front_of_me__())
                self.assertTrue(player.can_see_puck())
                self.move_puck_to(orig_pos)

    def test_can_see_puck_rotations(self):
        """ 'Seeing' the puck works?"""
        angles_to_try = randomsample(range(-90, 90), 50)
        angles_to_try.append(-90)
        angles_to_try.append(90)
        for _ in range(10):
            self.half_ice_rink.set_random_positions_for_agents()
            for an_angle in angles_to_try:
                orig_pos = self.half_ice_rink.puck.pos
                for player in self.half_ice_rink.defense + self.half_ice_rink.attack:
                    self.move_puck_to(player.__pt_in_front_of_me__())
                    v = player.__vector_me_to_puck__()
                    v.rotate(an_angle)
                    self.move_puck_to(player.pos)
                    self.half_ice_rink.puck.pos.translate_following(v)
                    self.assertTrue(player.can_see_puck(),
                                    "I can't see a puck that is  at an angle of %.2f (radians) of me" % (an_angle))
                    self. move_puck_to(orig_pos)

    def test_can_reach_puck(self):
        """ 'Reaching' the puck works?"""

        for _ in range(10):
            self.half_ice_rink.set_random_positions_for_agents()
            orig_pos = copy(self.half_ice_rink.puck.pos)
            for player in self.half_ice_rink.defense + self.half_ice_rink.attack:
                # (*) player is on the same position as puck
                self.move_puck_to(player.pos)
                self.assertTrue(player.can_reach_puck())
                # if I can reach it, then I can see it!
                self.assertTrue(player.can_see_puck())
                self.move_puck_to(orig_pos)
                # (*) if puck is too far, I can't reach it
                d_to_puck = player.model.distance_to_puck(player.pos)
                # print("[my reach = %.2f feet] d to puck = %.2f feet" % (player.reach, d_to_puck))
                if (d_to_puck <= player.reach) and (player.angle_to_puck().value <= AngleInRadians.PI_HALF):
                    self.assertTrue(player.can_reach_puck(),
                                    "I CAN'T reach puck, even though distance to puck = %.2f feet (my reach is %.2f feet) and angle to puck is %s" % (d_to_puck, player.reach, player.angle_to_puck()))
                    # if I can reach it, then I can see it!
                    self.assertTrue(player.can_see_puck())
                else:
                    self.assertFalse(player.can_reach_puck(),
                                     "I CAN reach puck, even though distance to puck = %.2f feet (my reach is %.2f feet) and angle to puck is %s" % (d_to_puck, player.reach, player.angle_to_puck()))
                # (*) player can reach the puck if it is in "pt in front of him" (by definition)
                self.move_puck_to(player.__pt_in_front_of_me__())
                self.assertTrue(player.can_reach_puck())
                # if I can reach it, then I can see it!
                self.assertTrue(player.can_see_puck())
                self.move_puck_to(orig_pos)

    def test_can_grab_puck(self):
        """ 'Grabbing' the puck works?"""

        for _ in range(10):
            self.half_ice_rink.set_random_positions_for_agents()
            for player in self.half_ice_rink.defense + self.half_ice_rink.attack:
                if player.can_reach_puck():
                    self.assertTrue(player.grab_puck())

    def test_calculate_speed_and_direction(self):
        """Basic functionality for shooting and moving."""
        r = Player.direction_and_speed_from(a = HockeyAction.SHOOT_HARD_TO_LEFT_PI_TIMES_1_OVER_10,
                                            power=Player.MAX_POWER,
                                            looking_at=Y_UNIT_VECTOR)
        self.assertNotEqual(r, None)
        direction, speed = r
        self.assertEqual(speed, Player.SHOT_MAX_SPEED)
        self.assertNotEqual(direction, Y_UNIT_VECTOR)
        self.assertTrue(direction.x < Y_UNIT_VECTOR.x, "direction = %s" % (direction))
        self.assertTrue(direction.y < Y_UNIT_VECTOR.y, "direction = %s" % (direction))

        r = Player.direction_and_speed_from(a = HockeyAction.SHOOT_HARD_TO_RIGHT_PI_TIMES_1_OVER_10,
                                            power=Player.MAX_POWER,
                                            looking_at=Y_UNIT_VECTOR)
        self.assertNotEqual(r, None)
        direction, speed = r
        self.assertEqual(speed, Player.SHOT_MAX_SPEED)
        self.assertNotEqual(direction, Y_UNIT_VECTOR)
        self.assertTrue(direction.x > Y_UNIT_VECTOR.x, "direction = %s" % (direction))
        self.assertTrue(direction.y < Y_UNIT_VECTOR.y, "direction = %s" % (direction))
