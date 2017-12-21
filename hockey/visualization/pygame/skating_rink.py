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

    def __init__(self, ice_rink: SkatingIce):
        super().__init__()
        self.ice_rink = ice_rink
        self.converter = World2CanvasConverter(
            world_width=self.ice_rink.width, world_height=self.ice_rink.height, window_border=(10, 10))

    def representation(self) -> DrawingObjects:
        cells_in_sc = []
        for idx_x in range(0, self.ice_rink.width):
            for idx_y in range(1, self.ice_rink.height + 1):
                left_in_sc, top_in_sc = self.converter.world_tuple_2_screen(idx_x, idx_y)
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
