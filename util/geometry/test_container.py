#!/usr/bin/env python
"""Testing of particles moving on a container (ie, with walls).

"""

import unittest

import math
from random import randint, random
from geometry.point import Point
from geometry.vector import Vec2d
from util.geometry.container import Container
from util.base import random_between

from util.geometry.lines import StraightLine

class TestContainer(unittest.TestCase):
    """Testing particles moving on a container."""

    def setUp(self):
        """Initialization"""
        self.container = Container(height=85, width=100)

    def test(self):
        container = Container(height=4, width=4)
        initial_pt = Point(0,0)
        initial_speed = Vec2d(-5.4096,0)
        new_pt, new_direction = container.particle_move(for_how_long=1, particle_diameter=0, particle_pos=initial_pt, particle_speed_vector=initial_speed, friction_constant_opt=None)
        print("Travelling from %s at a speed of %s gets you to %s and the new speed is %s)" % (initial_pt, initial_speed, new_pt, new_direction))

        # self.assertAlmostEqual(new_pt.x, 4)
        # self.assertAlmostEqual(new_pt.y, 3)

    def random_vector(self, with_norm: float) -> Vec2d:
        unit_speed = Vec2d.origin_to(a_pt=Point(random(), random()))
        if random() < 0.5:
            unit_speed.x *= -1
        if random() < 0.5:
            unit_speed.y *= -1
        return unit_speed * with_norm

    def test_not_bouncing(self):
        for _ in range(50): # how many tests to run
            initial_speed = self.random_vector(with_norm = randint(0, 100) / 10)
            # agent will be placed somewhere where he CAN'T reach the walls in 1 step
            initial_x = randint(math.ceil(0 + abs(initial_speed.x)), math.floor(self.container.width - abs(initial_speed.x)))
            initial_y = randint(math.ceil(0 + abs(initial_speed.y)), math.floor(self.container.height - abs(initial_speed.y)))
            initial_pos = Point(initial_x, initial_y)
            length_of_movement = 1/20 # of a second
            new_pt, new_speed = self.container.particle_move(
                for_how_long=length_of_movement,
                particle_diameter = 1,
                particle_pos = initial_pos,
                particle_speed_vector = initial_speed,
                friction_constant_opt = None)

            self.assertAlmostEqual(
                new_pt.x,
                initial_pos.x + initial_speed.x * length_of_movement,
                msg = "initial pos: %s, initial speed: %s, result: %s" % (initial_pos, initial_speed, new_pt))
            self.assertAlmostEqual(
                new_pt.y,
                initial_pos.y + initial_speed.y * length_of_movement,
                msg = "initial pos: %s, initial speed: %s, result: %s" % (initial_pos, initial_speed, new_pt))
            # as there is no friction and I hit no wall, the speed stays the same:
            self.assertEqual(new_speed, initial_speed)

    def test_bouncing(self):
        for _ in range(100): # how many tests to run
            length_of_movement = randint(1, 40) / 10 # of a second
            # choose a speed vector non-zero on both directions:
            initial_speed = self.random_vector(with_norm = randint(0, 10) / 10)
            while initial_speed.x == 0 or initial_speed.y == 0:
                initial_speed = self.random_vector(with_norm = randint(0, 10) / 10)
            # agent will be placed somewhere where he WILL reach the walls in 1 step
            if random() < 0.5:
                # make it rebound from X wall, not Y
                delta_x = abs(initial_speed.x) * length_of_movement
                initial_x = \
                    random_between(self.container.width - delta_x, self.container.width) if initial_speed.x > 0 \
                        else random_between(0, delta_x)
                delta_y = abs(initial_speed.y) * length_of_movement
                initial_y = randint(math.ceil(0 + abs(delta_y)), math.floor(self.container.height - abs(delta_y)))
                initial_pos = Point(initial_x, initial_y)
                new_pt, new_speed = self.container.particle_move(
                    for_how_long=length_of_movement,
                    particle_diameter = 0,
                    particle_pos = initial_pos,
                    particle_speed_vector = initial_speed,
                    friction_constant_opt = None)
                conds_msg = "initial pos: %s, initial speed: %s, moved %.2f secs, result pos: %s, new speed: %s" % (initial_pos, initial_speed, length_of_movement, new_pt, new_speed)
                # print(conds_msg)
                # speed on x changed sign
                self.assertTrue(initial_speed.x * new_speed.x < 0, msg = conds_msg)
                # speed on y didn't change signs
                self.assertTrue(new_speed.y * initial_speed.y > 0, msg = conds_msg)
                # 'y' coordinates maintain certain consistency:
                self.assertTrue((new_pt.y - initial_pos.y) * (new_speed.y) > 0, msg = conds_msg)
            else:
                # make it rebound from Y wall, not X
                delta_y = abs(initial_speed.y) * length_of_movement
                initial_y = \
                    random_between(self.container.height - delta_y, self.container.height) if initial_speed.y > 0 \
                        else random_between(0, delta_y)
                delta_x = abs(initial_speed.x) * length_of_movement
                initial_x = randint(math.ceil(0 + abs(delta_x)), math.floor(self.container.width - abs(delta_x)))
                initial_pos = Point(initial_x, initial_y)
                new_pt, new_speed = self.container.particle_move(
                    for_how_long=length_of_movement,
                    particle_diameter = 0,
                    particle_pos = initial_pos,
                    particle_speed_vector = initial_speed,
                    friction_constant_opt = None)
                conds_msg = "initial pos: %s, initial speed: %s, moved %.2f secs, result pos: %s, new speed: %s" % (initial_pos, initial_speed, length_of_movement, new_pt, new_speed)
                # print(conds_msg)
                # speed on 'y' changed sign
                self.assertTrue(initial_speed.y * new_speed.y < 0, msg = conds_msg)
                # speed on 'x' didn't change signs
                self.assertTrue(new_speed.x * initial_speed.x > 0, msg = conds_msg)
                # 'x' coordinates maintain certain consistency:
                self.assertTrue((new_pt.x - initial_pos.x) * (new_speed.x) > 0, msg = conds_msg)



