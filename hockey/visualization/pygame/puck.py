from rendering.base import Color
from rendering.pygame.base import DrawingObjects, DrawingRect, DrawingCircle, DrawingLine, Renderable

from hockey.core.puck import Puck
from hockey.visualization.pygame.world_to_canvas import World2CanvasConverter


class PuckPygameRenderable(Renderable):
    def __init__(self, puck: Puck, w2c_converter: World2CanvasConverter):
        self.puck = puck
        super().__init__()
        self.converter = w2c_converter

    def representation(self) -> DrawingObjects:
        # screen cooordinates:
        top_in_wc = 0
        top_in_sc = self.converter.y_on_screen(top_in_wc)
        left_in_wc = 0
        left_in_sc = self.converter.x_on_screen(left_in_wc)
        rink = DrawingObjects(
            rects=[],
            circles=[
                DrawingCircle(
                    center=(self.converter.x_on_screen(self.puck.pos[0]), self.converter.y_on_screen(self.puck.pos[1])),
                    radius=self.converter.x_on_screen(self.puck.radius),
                    color=Color.WHITE,
                    line_thickness=2),
            ],
            lines=[
            ])
        return rink


if __name__ == "__main__":
    half_ice_rink = PuckPygameRenderable(puck=None)
    print(half_ice_rink)
