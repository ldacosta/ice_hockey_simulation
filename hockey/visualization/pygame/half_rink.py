from rendering.base import Color
from rendering.pygame.base import DrawingObjects, DrawingRect, DrawingCircle, DrawingLine, Renderable

from hockey.core.half_rink import HockeyHalfRink
from hockey.visualization.pygame.world_to_canvas import World2CanvasConverter
from hockey.visualization.pygame.puck import PuckPygameRenderable


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
        top_in_sc = self.converter.y_on_screen(top_in_wc)
        left_in_wc = 0 # self.X_MARGINS_WC/2
        left_in_sc = self.converter.x_on_screen(left_in_wc)
        right_in_sc = self.converter.x_on_screen(left_in_wc + self.half_rink.width)
        bottom_in_sc = self.converter.y_on_screen(top_in_wc + self.half_rink.height)
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
                        center=(left_in_sc, self.converter.y_on_screen(top_in_wc + self.half_rink.HEIGHT_ICE/2)),
                        radius=self.converter.x_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                    # faceoff circles
                    # neutral zone
                    DrawingCircle(
                        center=(
                        self.converter.x_on_screen(left_in_wc + self.half_rink.NEUTRAL_FACEOFF_X), self.converter.y_on_screen(top_in_wc + self.half_rink.FACEOFF_TOP_Y)),
                        radius=self.converter.x_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                    DrawingCircle(
                        center=(
                        self.converter.x_on_screen(left_in_wc + self.half_rink.NEUTRAL_FACEOFF_X), self.converter.y_on_screen(top_in_wc + self.half_rink.FACEOFF_BOTTOM_Y)),
                        radius=self.converter.x_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                    # offensive zone
                    DrawingCircle(
                        center=(
                        self.converter.x_on_screen(left_in_wc + self.half_rink.OFF_FACEOFF_X), self.converter.y_on_screen(top_in_wc + self.half_rink.FACEOFF_TOP_Y)),
                        radius=self.converter.x_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                    DrawingCircle(
                        center=(
                            self.converter.x_on_screen(left_in_wc + self.half_rink.OFF_FACEOFF_X),
                            self.converter.y_on_screen(top_in_wc + self.half_rink.FACEOFF_BOTTOM_Y)),
                        radius=self.converter.x_on_screen(15),
                        color=Color.WHITE,
                        line_thickness=2),
                ],
                lines=[
                    # half of the rink
                    DrawingLine(
                        begin=(left_in_sc, top_in_sc),
                        end=(left_in_sc, top_in_sc + self.converter.y_on_screen(self.half_rink.height)),
                        color=Color.RED,
                        thickness=2),
                    # blue line
                    DrawingLine(
                        begin=(left_in_sc + self.converter.x_on_screen(self.half_rink.BLUE_LINE_X), top_in_sc),
                        end=(left_in_sc + self.converter.x_on_screen(self.half_rink.BLUE_LINE_X), top_in_sc + self.converter.y_on_screen(self.half_rink.height)),
                        color=Color.BLUE,
                        thickness=2),
                    # goal
                    DrawingLine(
                        begin=(left_in_sc + self.converter.x_on_screen(self.half_rink.goal_position[0]), top_in_sc),
                        end=(left_in_sc + self.converter.x_on_screen(self.half_rink.goal_position[0]), bottom_in_sc),
                        color=Color.TOMATO,
                        thickness=1),
                    DrawingLine(
                        begin=(left_in_sc + self.converter.x_on_screen(self.half_rink.goal_position[0]), top_in_sc + self.converter.y_on_screen(self.half_rink.goal_position[1][0])),
                        end=(left_in_sc + self.converter.x_on_screen(self.half_rink.goal_position[0]), top_in_sc + self.converter.y_on_screen(self.half_rink.goal_position[1][1])),
                        color=Color.RED,
                        thickness=3),
                ])
        puck = PuckPygameRenderable(puck=self.half_rink.puck, w2c_converter=self.converter).representation()
        return rink + puck


if __name__ == "__main__":
    half_ice_rink = HalfRinklPygameRenderable(half_rink=None)
    print(half_ice_rink)
