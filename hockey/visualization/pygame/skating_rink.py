from functools import reduce

from rendering.base import Color
from rendering.pygame.base import DrawingObjects, DrawingRect, DrawingCircle, DrawingLine, Renderable

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
        # screen cooordinates:
        top_in_wc = 0 # self.Y_MARGINS_WC/2
        top_in_sc = self.converter.y_on_screen(top_in_wc)
        left_in_wc = 0 # self.X_MARGINS_WC/2
        left_in_sc = self.converter.x_on_screen(left_in_wc)
        right_in_sc = self.converter.x_on_screen(left_in_wc + self.ice_rink.width)
        bottom_in_sc = self.converter.y_on_screen(top_in_wc + self.ice_rink.height)
        zz = [DrawingRect(top=top_in_wc + idx_y,
                            left=left_in_wc + idx_x,
                            width=1,
                            height=1,
                            color=Color.TOMATO,
                            lines_thickness=3) for idx_x in range(0, self.ice_rink.width) for idx_y in range(0, self.ice_rink.height)]
        ll = [DrawingRect(top=self.converter.y_on_screen(top_in_wc + idx_y),
                            left=self.converter.x_on_screen(left_in_wc + idx_x),
                            width=self.converter.x_on_screen(1),
                            height=self.converter.y_on_screen(1),
                            color=Color.TOMATO,
                            lines_thickness=3) for idx_x in range(0, self.ice_rink.width) for idx_y in range(0, self.ice_rink.height)]
        rink = DrawingObjects(
                rects=ll,
            # [
            #     DrawingRect(top=top_in_sc,
            #                 left=left_in_sc,
            #                 width= right_in_sc - left_in_sc,
            #                 height=bottom_in_sc-top_in_sc,
            #                 color=Color.WHITE,
            #                 lines_thickness=3)],
                circles=[
                    # # half-circle of half of the rink
                    # DrawingCircle(
                    #     center=(left_in_sc, self.converter.y_on_screen(top_in_wc + self.ice_rink.height / 2)),
                    #     radius=self.converter.x_on_screen(15),
                    #     color=Color.WHITE,
                    #     line_thickness=2),
                    # # faceoff circles
                    # # neutral zone
                    # DrawingCircle(
                    #     center=(
                    #         self.converter.x_on_screen(left_in_wc + self.ice_rink.NEUTRAL_FACEOFF_X), self.converter.y_on_screen(top_in_wc + self.ice_rink.FACEOFF_TOP_Y)),
                    #     radius=self.converter.x_on_screen(15),
                    #     color=Color.WHITE,
                    #     line_thickness=2),
                    # DrawingCircle(
                    #     center=(
                    #         self.converter.x_on_screen(left_in_wc + self.ice_rink.NEUTRAL_FACEOFF_X), self.converter.y_on_screen(top_in_wc + self.ice_rink.FACEOFF_BOTTOM_Y)),
                    #     radius=self.converter.x_on_screen(15),
                    #     color=Color.WHITE,
                    #     line_thickness=2),
                    # # offensive zone
                    # DrawingCircle(
                    #     center=(
                    #         self.converter.x_on_screen(left_in_wc + self.ice_rink.OFF_FACEOFF_X), self.converter.y_on_screen(top_in_wc + self.ice_rink.FACEOFF_TOP_Y)),
                    #     radius=self.converter.x_on_screen(15),
                    #     color=Color.WHITE,
                    #     line_thickness=2),
                    # DrawingCircle(
                    #     center=(
                    #         self.converter.x_on_screen(left_in_wc + self.ice_rink.OFF_FACEOFF_X),
                    #         self.converter.y_on_screen(top_in_wc + self.ice_rink.FACEOFF_BOTTOM_Y)),
                    #     radius=self.converter.x_on_screen(15),
                    #     color=Color.WHITE,
                    #     line_thickness=2),
                ],
                lines=[
                    # # half of the rink
                    # DrawingLine(
                    #     begin=(left_in_sc, top_in_sc),
                    #     end=(left_in_sc, top_in_sc + self.converter.y_on_screen(self.ice_rink.height)),
                    #     color=Color.RED,
                    #     thickness=2),
                    # # blue line
                    # DrawingLine(
                    #     begin=(left_in_sc + self.converter.x_on_screen(self.ice_rink.BLUE_LINE_X), top_in_sc),
                    #     end=(left_in_sc + self.converter.x_on_screen(self.ice_rink.BLUE_LINE_X), top_in_sc + self.converter.y_on_screen(self.ice_rink.height)),
                    #     color=Color.BLUE,
                    #     thickness=2),
                    # # goal
                    # DrawingLine(
                    #     begin=(left_in_sc + self.converter.x_on_screen(self.ice_rink.goal_position[0]), top_in_sc),
                    #     end=(left_in_sc + self.converter.x_on_screen(self.ice_rink.goal_position[0]), bottom_in_sc),
                    #     color=Color.TOMATO,
                    #     thickness=1),
                    # DrawingLine(
                    #     begin=(left_in_sc + self.converter.x_on_screen(self.ice_rink.goal_position[0]), top_in_sc + self.converter.y_on_screen(self.ice_rink.goal_position[1][0])),
                    #     end=(left_in_sc + self.converter.x_on_screen(self.ice_rink.goal_position[0]), top_in_sc + self.converter.y_on_screen(self.ice_rink.goal_position[1][1])),
                    #     color=Color.RED,
                    #     thickness=3),
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

if __name__ == "__main__":
    half_ice_rink = SkatingRinklPygameRenderable(ice_rink=None)
    print(half_ice_rink)
