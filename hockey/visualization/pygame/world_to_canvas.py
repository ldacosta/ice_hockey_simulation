# -*- coding: utf-8 -*-
"""Conversion of world 2 canvas.

TODO:

"""

import math
import tkinter as tk
import numpy as np
from typing import Tuple, Optional

from geometry.point import Point


class World2CanvasConverter(object):
    """
    Handles conversions from a world to a canvas.
    Assumes:
        * window has (0,0) on top-left.
        * canvas lives inside window (ie, on its coordinates' system).
        * world has (0,0) on bottom-right.
    """

    @classmethod
    def screen_width_height(cls) -> Tuple[int, int]:
        "Returns width and height of current screen."
        root = tk.Tk()
        return (root.winfo_screenwidth(), root.winfo_screenheight())

    def __init__(self,
                 world_X_limits: Tuple[float, float], world_Y_limits: Tuple[float, float],
                 window_width_border: Optional[float] = 0,
                 window_height_border: Optional[float] = 0,
                 proposed_canvas_height_opt: Optional[float] = None, proposed_canvas_width_opt: Optional[float] = None):
        self.x_min, self.x_max =  world_X_limits
        self.y_min, self.y_max =  world_Y_limits
        assert self.x_min < self.x_max
        assert self.y_min < self.y_max
        (max_window_width, max_window_height) = World2CanvasConverter.screen_width_height()
        max_window_width *= .75
        max_window_height *= .75
        max_canvas_width = max_window_width - 2 * (window_width_border or 0)
        max_canvas_height = max_window_height - 2 * (window_height_border or 0)
        print("[MAX window] width = %d, height = %d => MAX canvas:  width = %d, height = %d" % (max_window_width, max_window_height, max_canvas_width, max_canvas_height))
        assert (proposed_canvas_height_opt is None) or (proposed_canvas_height_opt <= max_canvas_height)
        assert (proposed_canvas_width_opt is None) or (proposed_canvas_width_opt <= max_canvas_width)
        self.world_width = self.x_max - self.x_min
        self.world_height = self.y_max - self.y_min
        # I need to find MAX screen width and height such that
        # (world_width/world_height) == (screen_width/screen_height)
        # let's say that I choose screen width as max_width. What is the value of the height?
        possible_width = max_canvas_width if proposed_canvas_width_opt is None else proposed_canvas_width_opt
        possible_height = (self.world_height * possible_width) / self.world_width
        if possible_height <= max_canvas_height:
            # sold!
            self.canvas_width = possible_width
            self.canvas_height = possible_height
        else:
            # let's say that I choose screen height as max_height. What is the value of the width?
            possible_height = max_canvas_height if proposed_canvas_height_opt is None else proposed_canvas_height_opt
            possible_width = (self.world_width * possible_height) / self.world_height
            if possible_width <= max_canvas_width:
                # sold!
                self.canvas_width = possible_width
                self.canvas_height = possible_height
            else:
                raise RuntimeError(
                    "Impossible to create a canvas with proposed height = %.2f or width = %.2f (maxs for screen are height = %.2f and width = %.2f)" %
                    (possible_height, possible_width, max_canvas_height, max_canvas_width))
        self.screen_width = int(math.floor(self.canvas_width + 2 * window_width_border))
        self.screen_height = int(math.floor(self.canvas_height + 2 * window_height_border))
        # create world 2 canvas conversion matrix:
        a = self.canvas_width / self.world_width
        b = self.canvas_height / self.world_height
        self.transformation_matrix = np.zeros((3,3))
        self.transformation_matrix[0][0] = a
        self.transformation_matrix[0][2] = window_width_border + -a * self.x_min
        self.transformation_matrix[1][1] = -b
        self.transformation_matrix[1][2] = window_height_border + b * self.y_max
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
               "Screen: width = %.2f, height = %.2f" % (self.canvas_width, self.canvas_height)

    def length_on_screen(self, length_on_world: float) -> float:
        "Given a length on world returns the length on the screen."
        world_pt = Point(length_on_world, length_on_world)
        result = self.world_pt_2_screen(world_pt)
        world_orig_on_screen = self.world_pt_2_screen(Point(0, 0))
        screen_dist_x = abs(result.x - world_orig_on_screen.x)
        screen_dist_y = abs(result.y - world_orig_on_screen.y)
        msg = "[Distance on world is %.2f] Screen distance is %.2f in X, %.2f in Y" % (length_on_world, screen_dist_x, screen_dist_y)
        assert abs(screen_dist_x -screen_dist_y) < 1e-6, msg # TODO: get rid of this sanity check once everything is stable.
        return screen_dist_x
