import abc
import uuid

from mesa import Agent
from typing import Optional
from geometry.point import Point
from geometry.vector import Vec2d
from hockey.core.model import TIME_PER_FRAME

class ObjectOnIce(Agent):
    """Anything that goes on ice follows this behaviour."""
    def __init__(self,
                 prefix_on_id: str,
                 hockey_world_model,
                 size: float,
                 pos_opt: Optional[Point] = None,
                 speed_opt: Optional[Vec2d] = None):
        super().__init__(unique_id=prefix_on_id + "_" + str(uuid.uuid4()), model=hockey_world_model)
        if (pos_opt is None):
            self.pos = self.model.get_random_position()
        else:
            self.pos = pos_opt
        if (speed_opt is None):
            self.speed = Vec2d(0, 0)
        else:
            self.speed = speed_opt
        self.size = size

    def is_moving(self) -> bool:
        return not self.speed.is_zero()

    def move_by_bouncing_from_walls(self):
        half_size = self.size/2
        def handle_walls(curr_position: float, curr_speed: float, min_value: float, max_value: float) -> (float, float):
            new_position = curr_position + curr_speed * TIME_PER_FRAME
            new_speed = curr_speed
            if new_position <= (min_value + half_size):
                new_position = 2 * (min_x + half_size) - new_position
                new_speed *= -1
            elif new_position >= (max_value - half_size):
                # formula is: (max_value - self.size) - (new_position - (max_value - self.size))
                new_position = 2 * (max_value - half_size) - new_position
                new_speed *= -1
            return (new_position, new_speed)

        curr_x, curr_y = self.pos
        if (curr_y >= self.model.GOALIE_Y_BOTTOM) and (curr_y <= self.model.GOALIE_Y_TOP):
            if (curr_x >= self.model.GOALIE_X):
                min_x = self.model.GOALIE_X
                max_x = self.model.space.width
            else:
                min_x = 0
                max_x = self.model.GOALIE_X
        else:
            min_x = 0
            max_x = self.model.space.width
        (new_x, new_speed_x) = handle_walls(
            curr_position=curr_x,
            curr_speed=self.speed[0],
            min_value = min_x,
            max_value=max_x)
        (new_y, new_speed_y) = handle_walls(
            curr_position=curr_y,
            curr_speed=self.speed[1],
            min_value = 0,
            max_value=self.model.space.height)
        # If you need debugging info, un-comment this:
        # print("[%s] current: pos => (%f,%f), speed => (%f,%f); in %f seconds, moving to: pos => (%f,%f), new speed => (%f,%f)" %
        #       (self.unique_id, self.pos[0], self.pos[1], self.speed[0], self.speed[1], TIME_PER_FRAME, new_x, new_y, new_speed_x, new_speed_y))
        try:
            self.model.space.move_agent(self, Point(new_x, new_y))
        except Exception as e:
            print("hello")
            raise e
        self.speed = Vec2d.origin_to(Point(new_speed_x, new_speed_y)) # Vector2D.from_tip ((new_speed_x, new_speed_y))

    @abc.abstractmethod
    def move_around(self):
        pass
