# -*- coding: utf-8 -*-
"""Definition of a skating rink.

TODO:

"""

from functools import reduce

from rendering.base import Color
from rendering.pygame.base import DrawingObjects, DrawingRect, Renderable

from hockey.core.ice_surface.no_obstacles import SkatingIce
from hockey.visualization.pygame.player import PlayerPygameRenderable
from hockey.visualization.pygame.puck import PuckPygameRenderable
from hockey.visualization.pygame.world_to_canvas import World2CanvasConverter


class SkatingRinklPygameRenderable(Renderable):

    X_MARGINS_WC = 10 # total margins on X, in world coordinates
    Y_MARGINS_WC = 10 # total margins on Y, in world coordinates

    def __init__(self, ice_rink: SkatingIce):
        self.ice_rink = ice_rink
        super().__init__()
        self.converter = World2CanvasConverter(
            world_width=self.ice_rink.width + self.X_MARGINS_WC, world_height=self.ice_rink.height + self.Y_MARGINS_WC)

    def representation(self) -> DrawingObjects:
        top_in_wc = 0 # self.Y_MARGINS_WC/2
        # top_in_sc = self.converter.y_on_screen(top_in_wc)
        left_in_wc = 0 # self.X_MARGINS_WC/2
        # left_in_sc = self.converter.length_on_screen(left_in_wc)
        # right_in_sc = self.converter.length_on_screen(left_in_wc + self.ice_rink.width)
        # bottom_in_sc = self.converter.y_on_screen(top_in_wc + self.ice_rink.height)
        cells_in_sc = []
        for idx_x in range(0, self.ice_rink.width):
            for idx_y in range(0, self.ice_rink.height):
                left_in_sc, top_in_sc = self.converter.world_tuple_2_screen(left_in_wc + idx_x, top_in_wc + idx_y)
                cells_in_sc.append(DrawingRect(top=top_in_sc,
                          left=left_in_sc,
                          width=self.converter.length_on_screen(1),
                          height=self.converter.length_on_screen(1),
                          color=Color.TOMATO,
                          lines_thickness=3))
        rink = DrawingObjects(
                rects=cells_in_sc,
                circles=[
                ],
                lines=[
                ])
        puck = PuckPygameRenderable(puck=self.ice_rink.puck, w2c_converter=self.converter).representation()
        all_defense_players = reduce(
            lambda repr1, repr2: repr1 + repr2,
            [PlayerPygameRenderable(a_def, w2c_converter=self.converter).representation() for a_def in self.ice_rink.defense],
            DrawingObjects(rects=[], circles=[], lines=[]))
        all_offensive_players = reduce(
            lambda repr1, repr2: repr1 + repr2,
            [PlayerPygameRenderable(a_def, w2c_converter=self.converter).representation() for a_def in self.ice_rink.attack],
            DrawingObjects(rects=[], circles=[], lines=[]))
        return rink + puck + all_defense_players + all_offensive_players
