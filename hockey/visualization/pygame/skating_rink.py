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
            world_X_limits=(-0.5,self.ice_rink.width + 0.5), world_Y_limits=(-0.5, self.ice_rink.height + 0.5),
            window_width_border=100, window_height_border=10)

    def representation(self) -> DrawingObjects:
        cells_in_sc = []
        # we are making squares of side 1
        for x_in_world in range(0, self.ice_rink.width):
            for y_in_world in range(1, self.ice_rink.height + 1):
                x_in_sc, y_in_sc = self.converter.world_tuple_2_screen(x_in_world - 0.5, y_in_world - 0.5)
                cells_in_sc.append(DrawingRect(top=y_in_sc,
                          left=x_in_sc,
                          width=self.converter.length_on_screen(1),
                          height=self.converter.length_on_screen(1),
                          color=Color.GREEN,
                          lines_thickness=1))
        rink = DrawingObjects(rects=cells_in_sc, circles=[], lines=[])
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
