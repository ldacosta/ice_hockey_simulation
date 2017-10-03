from hockey.core.player import Player, Defense, Forward
from rendering.pygame.base import Renderable, DrawingObjects, DrawingCircle, DrawingLine
from rendering.base import Color
from hockey.visualization.pygame.world_to_canvas import World2CanvasConverter

class PlayerPygameRenderable(Renderable):

    def __init__(self, player: Player, w2c_converter: World2CanvasConverter):
        self.player = player
        super().__init__()
        self.converter = w2c_converter

    def representation(self) -> DrawingObjects:
        end_of_speed_vector = self.player.pos.clone().translate_following(self.player.size * self.player.speed.normalized())
        if isinstance(self.player, Defense):
            color = Color.BLUE # self.player.colour,
        elif isinstance(self.player, Forward):
            color = Color.RED # self.player.colour,
        else:
            raise RuntimeError("I don't know this kind of player.")
        return DrawingObjects(
            rects=[],
            circles=[ # actual position
                DrawingCircle(
                    center=(self.converter.x_on_screen(self.player.pos[0]), self.converter.y_on_screen(self.player.pos[1])),
                    radius=self.converter.x_on_screen(self.player.size/2),
                    color=color,
                    line_thickness=2),
            ],
            lines=[ # direction
                DrawingLine(
                    begin=(self.converter.x_on_screen(self.player.pos[0]), self.converter.y_on_screen(self.player.pos[1])),
                    end=(self.converter.x_on_screen(end_of_speed_vector[0]), self.converter.y_on_screen(end_of_speed_vector[1])),
                    color=color,
                    thickness=6)])