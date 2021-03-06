from functools import reduce

from geometry.point import Point
from rendering.base import Color
from rendering.pygame.base import DrawingObjects, DrawingRect, DrawingCircle, DrawingLine, Renderable

from hockey.core.ice_surface.half_rink import HockeyHalfRink
from hockey.visualization.pygame.player import PlayerPygameRenderable
from hockey.visualization.pygame.puck import PuckPygameRenderable
from hockey.visualization.pygame.world_to_canvas import World2CanvasConverter


class HalfRinklPygameRenderable(Renderable):

    X_MARGINS_WC = 10 # total margins on X, in world coordinates
    Y_MARGINS_WC = 10 # total margins on Y, in world coordinates

    def __init__(self, half_rink: HockeyHalfRink):
        self.half_rink = half_rink
        super().__init__()
        self.converter = World2CanvasConverter(
            world_width=self.half_rink.width + self.X_MARGINS_WC, world_height=self.half_rink.height + self.Y_MARGINS_WC)

    def representation(self) -> DrawingObjects:
        # screen cooordinates:
        top_in_wc = 0 # self.Y_MARGINS_WC/2
        bottom_in_wc = top_in_wc + self.half_rink.height
        # top_in_sc = self.converter.y_on_screen(top_in_wc)
        left_in_wc = 0 # self.X_MARGINS_WC/2
        right_in_wc = left_in_wc + self.half_rink.width
        # left_in_sc = self.converter.length_on_screen(left_in_wc)
        # right_in_sc = self.converter.length_on_screen(left_in_wc + self.half_rink.width)
        # bottom_in_sc = self.converter.y_on_screen(top_in_wc + self.half_rink.height)


        left_in_sc, top_in_sc = self.converter.world_pt_2_screen(Point(top_in_wc, left_in_wc))
        right_in_sc, bottom_in_sc = self.converter.world_pt_2_screen(Point(right_in_wc, bottom_in_wc))

        rink = DrawingObjects(
                rects=[
                DrawingRect(top=top_in_sc,
                            left=left_in_sc,
                            width= right_in_sc - left_in_sc,
                            height=bottom_in_sc-top_in_sc,
                            color=Color.WHITE,
                            lines_thickness=3)],
                circles=[
                    # half-circle of half of the rink
                    DrawingCircle(
                        center=self.converter.world_tuple_2_screen(
                            left_in_wc,
                                  top_in_wc + self.half_rink.height/2),
                        radius=self.converter.length_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                    # faceoff circles
                    # neutral zone
                    DrawingCircle(
                        center=self.converter.world_pt_2_screen(
                            Point(left_in_wc + self.half_rink.NEUTRAL_FACEOFF_X,
                                  top_in_wc + self.half_rink.FACEOFF_TOP_Y).as_tuple()).as_tuple(),
                        radius=self.converter.length_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                    DrawingCircle(
                        center=(
                            self.converter.world_pt_2_screen(Point(left_in_wc + self.half_rink.NEUTRAL_FACEOFF_X,
                                                                   top_in_wc + self.half_rink.FACEOFF_BOTTOM_Y).as_tuple()).as_tuple()),
                        radius=self.converter.length_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                    # offensive zone
                    DrawingCircle(
                        center=self.converter.world_pt_2_screen(
                            Point(left_in_wc + self.half_rink.OFF_FACEOFF_X,
                                  top_in_wc + self.half_rink.FACEOFF_TOP_Y).as_tuple()).as_tuple(),
                        radius=self.converter.length_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                    DrawingCircle(
                        center=self.converter.world_pt_2_screen(
                            Point(left_in_wc + self.half_rink.OFF_FACEOFF_X,
                                  top_in_wc + self.half_rink.FACEOFF_BOTTOM_Y).as_tuple()).as_tuple(),
                        radius=self.converter.length_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                ],
                lines=[
                    # half of the rink
                    DrawingLine(
                        begin=self.converter.world_tuple_2_screen(left_in_wc, top_in_wc),
                        end=self.converter.world_tuple_2_screen(left_in_wc, top_in_wc + self.half_rink.height),
                        color=Color.RED,
                        thickness=2),
                    # blue line
                    DrawingLine(
                        begin=self.converter.world_tuple_2_screen(left_in_wc + self.half_rink.BLUE_LINE_X, top_in_wc),
                        end=self.converter.world_tuple_2_screen(
                            left_in_wc + self.half_rink.BLUE_LINE_X,
                            top_in_wc + self.half_rink.height),
                        color=Color.BLUE,
                        thickness=2),
                    # goal
                    DrawingLine(
                        begin=self.converter.world_tuple_2_screen(left_in_wc + self.half_rink.goal_position[0], top_in_wc),
                        end=self.converter.world_tuple_2_screen(
                            left_in_wc + self.half_rink.goal_position[0],
                            bottom_in_wc),
                        color=Color.TOMATO,
                        thickness=1),
                    DrawingLine(
                        begin=self.converter.world_tuple_2_screen(
                            left_in_wc + self.half_rink.goal_position[0],
                            top_in_wc + self.half_rink.goal_position[1][0]),
                        end=self.converter.world_tuple_2_screen(
                            left_in_wc + self.half_rink.goal_position[0],
                            top_in_wc + self.half_rink.goal_position[1][1]),
                        color=Color.RED,
                        thickness=3),
                ])
        puck = PuckPygameRenderable(puck=self.half_rink.puck, w2c_converter=self.converter).representation()
        all_defense_players = reduce(
            lambda repr1, repr2: repr1 + repr2,
            [PlayerPygameRenderable(a_def, w2c_converter=self.converter).representation() for a_def in self.half_rink.defense],
            DrawingObjects(rects=[], circles=[], lines=[]))
        all_offensive_players = reduce(
            lambda repr1, repr2: repr1 + repr2,
            [PlayerPygameRenderable(a_def, w2c_converter=self.converter).representation() for a_def in self.half_rink.attack],
            DrawingObjects(rects=[], circles=[], lines=[]))
        return rink + puck + all_defense_players + all_offensive_players

if __name__ == "__main__":
    half_ice_rink = HalfRinklPygameRenderable(half_rink=None)
    print(half_ice_rink)
