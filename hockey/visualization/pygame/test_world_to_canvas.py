# -*- coding: utf-8 -*-
"""Base class for Rendering on pygame.

TODO:

"""

import unittest
import math
from random import randint

from geometry.point import Point

from hockey.visualization.pygame.world_to_canvas import World2CanvasConverter

class TestWorld2Canvas(unittest.TestCase):
    """Testing transformations of world 2 canvas."""

    def setUp(self):
        """Initialization"""
        self.transformer = World2CanvasConverter(world_height=100, world_width=50)

    def test_limits(self):
        print(self.transformer)
        # origin
        world_origin = Point(0, 0)
        result = self.transformer.world_pt_2_screen(world_origin)
        self.assertAlmostEqual(result.x, 0)
        self.assertAlmostEqual(result.y, self.transformer.screen_height)
        # bottom left
        world_bottom_left = Point(self.transformer.world_width, self.transformer.world_height)
        result = self.transformer.world_pt_2_screen(world_bottom_left)
        self.assertAlmostEqual(result.x, self.transformer.screen_width)
        self.assertAlmostEqual(result.y, 0)

    def test_belonging_of_transformed(self):
        "Points inside the world should get transformed to points inside the screen."
        for _ in range(10):
            world_x = randint(0, int(math.floor(self.transformer.world_width)))
            world_y = randint(0, int(math.floor(self.transformer.world_height)))
            world_pt = Point(world_x, world_y)
            result = self.transformer.world_pt_2_screen(world_pt)
            msg = "World pt %s got converted into screen point %s" % (world_pt, result)
            self.assertTrue(result.x >= 0 and result.x <= self.transformer.screen_width, msg)
            self.assertTrue(result.y >= 0 and result.y <= self.transformer.screen_height, msg)

    def test_homogeneous_coordinates(self):
        "Points with same coordinates should stay that way."
        for _ in range(10):
            a_value = randint(0, min(int(math.floor(self.transformer.world_width)), int(math.floor(self.transformer.world_width))))
            world_pt = Point(a_value, a_value)
            result = self.transformer.world_pt_2_screen(world_pt)
            msg = "World pt %s got converted into screen point %s" % (world_pt, result)
            world_orig_on_screen = self.transformer.world_pt_2_screen(Point(0, 0))
            screen_dist_x = abs(result.x - world_orig_on_screen.x)
            screen_dist_y = abs(result.y - world_orig_on_screen.y)
            self.assertAlmostEqual(screen_dist_x, screen_dist_y, msg=msg)
