from hockey.core.player.base import Player
from hockey.core.player.defense import Defense
from hockey.core.player.forward import Forward
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
                    center=self.converter.world_pt_2_screen(self.player.pos).as_tuple(),
                    radius=self.converter.length_on_screen(self.player.size / 2),
                    color=color,
                    line_thickness=2),
            ],
            lines=[ # direction
                DrawingLine(
                    begin=self.converter.world_pt_2_screen(self.player.pos).as_tuple(),
                    end=self.converter.world_tuple_2_screen(end_of_speed_vector.x, end_of_speed_vector.y),
                    color=color,
                    thickness=6)])