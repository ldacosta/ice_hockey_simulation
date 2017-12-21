# -*- coding: utf-8 -*-
"""Conversion of world 2 canvas.

TODO:

"""

import tkinter as tk
import numpy as np

from typing import Tuple

from geometry.point import Point
from util.base import normalize_to


class World2CanvasConverter(object):
    """
    Handles conversions from a world to a canvas.
    Assumes:
        * canvas has (0,0) on top-left.
        * world has (0,0) on bottom-right.
    """

    X_MARGIN = 20
    Y_MARGIN = 20

    @classmethod
    def screen_width_height(cls) -> Tuple[int, int]:
        "Returns width and height of current screen."
        root = tk.Tk()
        return (root.winfo_screenwidth(), root.winfo_screenheight())

    def __init__(self,
                 world_width: float, world_height: float):
        (max_width, max_height) = World2CanvasConverter.screen_width_height()
        print("[screen detection] calculated width = %d, height = %d" % (max_width, max_height))
        self.world_width = world_width
        self.world_height = world_height
        # I need to find MAX screen width and height such that
        # (world_width/world_height) == (screen_width/screen_height)
        # let's say that I choose screen width as max_width. What is the value of the height?
        possible_width = max_width
        possible_height = (self.world_height * possible_width) / self.world_width
        if possible_height <= max_height:
            # sold!
            self.screen_width = possible_width
            self.screen_height = possible_height
        else:
            # let's say that I choose screen height as max_height. What is the value of the width?
            possible_height = max_height
            possible_width = (self.world_width * possible_height) / self.world_height
            if possible_width <= max_width:
                # sold!
                self.screen_width = possible_width
                self.screen_height = possible_height
            else:
                raise RuntimeError("what happened here???")
        # self.size_multiplier = int(min([max_height/self.world_height, max_width/self.world_width]))
        # self.screen_width = self.world_width * self.size_multiplier
        # self.screen_height = self.world_height * self.size_multiplier
        a = self.screen_width / self.world_width
        b = self.screen_height / self.world_height
        self.transformation_matrix = np.zeros((3,3))
        self.transformation_matrix[0][0] = a
        self.transformation_matrix[1][1] = -b
        self.transformation_matrix[1][2] = self.screen_height
        self.transformation_matrix[2][2] = 1


    def world_tuple_2_screen(self, x: float, y: float) -> Tuple[float, float]:
        "Transforms a tuple (representing a point) in world to a point in screen."
        return self.world_pt_2_screen(pt_world=Point(x,y)).as_tuple()

    def world_pt_2_screen(self, pt_world: Point) -> Point:
        "Transforms a point in world to a point in screen."
        pt = np.ones((3, 1))
        pt[0] = pt_world.x
        pt[1] = pt_world.y
        result = np.dot(self.transformation_matrix, pt)
        return Point(x=result[0][0], y=result[1][0])

    def __str__(self):
        return "World:  width = %.2f, height = %.2f\n" % (self.world_width, self.world_height) + \
               "Screen: width = %.2f, height = %.2f" % (self.screen_width, self.screen_height)

    def length_on_screen(self, length_on_world: float) -> float:
        "Given a lenght on world returns the length on the screen."
        world_pt = Point(length_on_world, length_on_world)
        result = self.world_pt_2_screen(world_pt)
        world_orig_on_screen = self.world_pt_2_screen(Point(0, 0))
        screen_dist_x = abs(result.x - world_orig_on_screen.x)
        screen_dist_y = abs(result.y - world_orig_on_screen.y)
        msg = "[Distance on world is %.2f] Screen distance is %.2f in X, %.2f in Y" % (length_on_world, screen_dist_x, screen_dist_y)
        assert screen_dist_x == screen_dist_y, msg # TODO: get rid of this sanity check once everything is stable.
        return screen_dist_x
