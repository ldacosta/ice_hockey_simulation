import abc
import uuid

from mesa import Agent
from typing import Tuple

from hockey.core.model import TIME_PER_FRAME
from util.geometry.vector import Vector2D, NULL_2D_VECTOR


class ObjectOnIce(Agent):
    """Anything that goes on ice follows this behaviour."""
    def __init__(self,
                 prefix_on_id: str,
                 hockey_world_model,
                 pos: Tuple[float, float] = (0.0, 0.0),
                 speed: Vector2D = NULL_2D_VECTOR):
        super().__init__(unique_id=prefix_on_id + "_" + str(uuid.uuid4()), model=hockey_world_model)
        self.pos = pos
        self.speed = speed

    def is_moving(self) -> bool:
        return self.speed.is_zero()

    def move_by_bouncing_from_walls(self):
        def handle_walls(curr_position: float, curr_speed: float, max_value: float) -> (float, float):
            new_position = curr_position + curr_speed * TIME_PER_FRAME
            new_speed = curr_speed
            if new_position < 0:
                new_position = -new_position # - 1
                new_speed *= -1
            elif new_position > max_value:
                new_position = max_value + (max_value - new_position) # + 1
                new_speed *= -1
            return (new_position, new_speed)

        (new_x, new_speed_x) = handle_walls(
            curr_position=self.pos[0],
            curr_speed=self.speed[0],
            max_value=self.model.space.width - 1)
        (new_y, new_speed_y) = handle_walls(
            curr_position=self.pos[1],
            curr_speed=self.speed[1],
            max_value=self.model.space.height - 1)
        # If you need debugging info, un-comment this:
        # print("[%s] current: pos => (%f,%f), speed => (%f,%f); in %f seconds, moving to: pos => (%f,%f), new speed => (%f,%f)" %
        #       (self.unique_id, self.pos[0], self.pos[1], self.speed[0], self.speed[1], TIME_PER_FRAME, new_x, new_y, new_speed_x, new_speed_y))
        self.model.space.move_agent(self, (new_x, new_y))
        self.speed = Vector2D.from_tip ((new_speed_x, new_speed_y))

    @abc.abstractmethod
    def move_around(self):
        pass