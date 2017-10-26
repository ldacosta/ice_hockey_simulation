import abc
import uuid

from random import random
from mesa import Agent
import numpy as np
from typing import Optional, Tuple
from geometry.point import Point
from geometry.vector import Vec2d
from hockey.core.model import TIME_PER_FRAME
from util.base import FEET_IN_METER, GRAVITY_ACCELERATION

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

    def move_by_bouncing_from_walls(self, prob_of_score_on_goal_opt: Optional[float] = None, friction_constant_opt: Optional[float] = None):
        """
        Moves around the ice, bouncing from walls and from the goal.
        Args:
            prob_of_score_on_goal: probability of score a goal if it comes to the front of the goal.

        Returns:

        """
        half_size = self.size/2
        def handle_walls(curr_position: float, curr_speed: float, min_value: float, max_value: float, goal_on_max: bool) -> Tuple[bool, Tuple[float, float]]:

            new_position = curr_position + curr_speed * TIME_PER_FRAME
            new_speed = curr_speed
            goal = False
            if new_position <= (min_value + half_size):
                new_position = 2 * (min_x + half_size) - new_position
                new_speed *= -1
            elif new_position >= (max_value - half_size):
                # this was a shot!
                if goal_on_max:
                    # sanity check
                    assert (prob_of_score_on_goal_opt is not None)
                    # ok then:
                    prob_of_score_on_goal = prob_of_score_on_goal_opt
                    self.model.shots += 1
                    if prob_of_score_on_goal > 0:
                        print("With probability %.2f we will see a goal now" % (prob_of_score_on_goal))
                        dice_throw = random()
                        if dice_throw <= prob_of_score_on_goal:
                            self.model.goals_scored += 1
                            print("GOOOOOOOOOOAAAAAAAAAALLLLL!!!!!!!!!!!!!!!!!!!!")
                            goal = True
                            new_position = 0
                            new_speed = 0
                        else:
                            print("No goal")
                if not goal:
                    # formula is: (max_value - self.size) - (new_position - (max_value - self.size))
                    new_position = 2 * (max_value - half_size) - new_position
                    new_speed *= -1

            return (goal, (new_position, new_speed))
        # First, apply deceleration because of friction
        if friction_constant_opt is not None:
            friction = friction_constant_opt
            # for reference: https://www.youtube.com/watch?v=y1kqH63-828
            if self.speed.x != 0:
                new_speed_x = np.sign(self.speed.x) * \
                              max(0.0, (abs(self.speed.x*FEET_IN_METER) - GRAVITY_ACCELERATION*friction)/FEET_IN_METER)
                self.speed.x = new_speed_x
            if self.speed.y != 0:
                new_speed_y = np.sign(self.speed.y) * \
                              max(0.0, (abs(self.speed.y*FEET_IN_METER) - GRAVITY_ACCELERATION*friction)/FEET_IN_METER)
                self.speed.y = new_speed_y
        #
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
        (is_goal, (new_x, new_speed_x)) = handle_walls(
            curr_position=curr_x,
            curr_speed=self.speed[0],
            min_value = min_x,
            max_value=max_x,
            goal_on_max=(prob_of_score_on_goal_opt is not None) and (max_x == self.model.GOALIE_X))
        if is_goal:
            new_y = 0
            new_speed_y = 0
        else:
            (is_goal, (new_y, new_speed_y)) = handle_walls(
                curr_position=curr_y,
                curr_speed=self.speed[1],
                min_value = 0,
                max_value=self.model.space.height,
                goal_on_max=False)
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
