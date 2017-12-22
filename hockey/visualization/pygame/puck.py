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
        rink = DrawingObjects(
            rects=[],
            circles=[
                DrawingCircle(
                    center=self.converter.world_pt_2_screen(self.puck.pos).as_tuple(),
                    radius=self.converter.length_on_screen(self.puck.radius),
                    color=Color.WHITE,
                    line_thickness=2),
            ],
            lines=[
            ])
        return rink
