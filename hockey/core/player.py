import abc
import math
import random

from typing import Tuple

from hockey.core.object_on_ice import ObjectOnIce
from util.base import normalize_to
from util.geometry.angle import AngleInRadians, rotatePoint
from util.geometry.vector import Vector2D, angle_between


class Player(ObjectOnIce):
    """Hockey Player."""

    # Remember: all speeds are in feet/second.
    MIN_SPEED_MOVING = 14
    MAX_SPEED_MOVING = 22
    MIN_SPEED_SPRINTING = 29
    MAX_SPEED_SPRINTING = 44
    #
    MIN_REACH = 3
    MAX_REACH = 6

    def __init__(self, prefix_on_id: str, hockey_world_model):
        self.angle_looking_at = AngleInRadians.random()
        self.moving_speed = normalize_to(
            random.random(),
            new_min = Player.MIN_SPEED_MOVING, new_max = Player.MAX_SPEED_MOVING,
            old_min = 0, old_max = 1)
        self.sprinting_speed = normalize_to(
            random.random(),
            new_min = Player.MIN_SPEED_SPRINTING, new_max = Player.MAX_SPEED_SPRINTING,
            old_min = 0, old_max = 1)
        self.current_speed = self.moving_speed
        super().__init__(prefix_on_id, hockey_world_model, pos=(0.0, 0.0), speed=self.speed_on_xy())
        self.reach = normalize_to(
            random.random(),
            new_min = Player.MIN_REACH, new_max = Player.MAX_REACH,
            old_min = 0, old_max = 1)
        self.have_puck = False

    def speed_on_xy(self) -> Vector2D:
        return self.vector_looking_at().scalar_multiply(self.current_speed)

    def move_around(self):
        # maybe irrealistic, but it'll do for now:
        self.move_by_bouncing_from_walls()

    def spin_around(self):
        self.angle_looking_at.randomly_mutate()
        print("%s: rotating to angle %s" % (self.unique_id, self.angle_looking_at))
        self.speed = self.speed_on_xy()


    def __vector_me_to_puck__(self) -> Vector2D:
        return Vector2D(pt_from=self.pos, pt_to=self.model.puck.pos)

    def __pt_in_front_of_me__(self) -> Tuple[float, float]:
        p0 = (self.pos[0] + self.reach, self.pos[1])  # looking at angle = 0
        return rotatePoint(centerPoint=self.pos, point=p0, angle=self.angle_looking_at)

    def can_reach_puck(self) -> bool:
        vector_me_to_puck = self.__vector_me_to_puck__()
        if vector_me_to_puck.norm() > self.reach: # puck too far
            return False
        else: # is it in front of me?
            # what is the point "just in front" of me?
            p_alpha = self.__pt_in_front_of_me__()
            # find the 2 points that make the diameter of the semi-circle in front of me:
            p_a = rotatePoint(centerPoint=self.pos, point=p_alpha, angle=AngleInRadians(value=math.pi / 2))
            p_b = rotatePoint(centerPoint=self.pos, point=p_alpha, angle=AngleInRadians.from_minus_pi_to_plus_pi(value=-math.pi / 2))
            # vector of the radius:
            v_radius = Vector2D(pt_from=p_a, pt_to=p_b)
            # ok, finally:
            the_angle = angle_between(v1 = v_radius, v2 = vector_me_to_puck)
            return the_angle.value <= math.pi


    def angle_to_puck(self) -> AngleInRadians:
        v_me_to_puck = self.__vector_me_to_puck__()
        v_front_of_me = self.vector_looking_at()
        return angle_between(v1=v_me_to_puck, v2=v_front_of_me)

    def can_see_puck(self) -> bool:
        v_me_to_puck = self.__vector_me_to_puck__()
        v_front_of_me = self.vector_looking_at()
        return (angle_between(v1=v_me_to_puck, v2=v_front_of_me) < AngleInRadians.PI_HALF) or \
               (angle_between(v1=v_front_of_me, v2=v_me_to_puck) < AngleInRadians.PI_HALF)

    def __wander_around__(self):
        self.move_around()
        if random.random() <= 0.10:
            self.spin_around()

    @abc.abstractmethod
    def act(self) -> bool:
        pass

    def turn_left(self):
        self.angle_looking_at += (math.pi / 2)

    def turn_right(self):
        self.angle_looking_at -= (math.pi / 2)

    def try_to_grab_puck(self):
        if not self.have_puck: # if I have it, no need to search!
            # is the puck free and close to me?
            if (not self.model.is_puck_taken()):
                if self.can_reach_puck():
                    # if I can reach puck, take it.
                    print("[%s] CAN REACH puck" % (self.unique_id))
                    self.have_puck = True
                    self.model.puck.is_taken = True
                elif self.can_see_puck():
                    print("[%s] I can see puck. Going towards it now" % (self.unique_id))
                    # Turn towards puck
                    print("I am looking at angle %s, angle to puck is %s, so I am turning to the sum of both" % (self.angle_looking_at, self.angle_to_puck()))
                    self.angle_looking_at += self.angle_to_puck()
                    # move a bit
                    self.move_around() # this assumes we can change direction AND move in 1 step. TODO: revise.
                else:
                    # I can neither reach or even see the puck
                    random_value = random.random()
                    if random_value < 0.33:
                        print("[%s] Can't reach OR see puck -> Turning left" % (self.unique_id))
                        self.turn_left()
                    elif random_value < 0.67:
                        print("[%s] Can't reach OR see puck -> Turning right" % (self.unique_id))
                        self.turn_right()
                    else:
                        print("[%s] Can't reach OR see puck -> Wandering about" % (self.unique_id))
                        self.__wander_around__()

            else:
                print("[%s] Puck TAKEN" % (self.unique_id))
                self.__wander_around__()

    def walk_around_with_puck(self):
        if not self.have_puck:
            self.try_to_grab_puck()
        else:
            self.move_around()
            # and I make the puck follow me:
            self.model.space.place_agent(self.model.puck, self.__pt_in_front_of_me__())

    def vector_looking_at(self) -> Vector2D:
        return Vector2D.from_angle(self.angle_looking_at)

    def step(self):
        self.act()


class Forward(Player):

    def __init__(self, hockey_world_model):
        super().__init__("forward", hockey_world_model)

    def act(self) -> bool:
        self.walk_around_with_puck() # for now
        return True
        # if not super().act():
        #     # this is only going to be
        #     # if I can see the goal, I shoot
        #     # TODO: ask for the probability of scoring first
        #     result = self.model.first_visible_goal_point_from(self.pos)
        #     if not result is None:
        #         pt_in_goal = result
        #         self.shoot_towards(pt_in_goal)
        #         return True
        #     else:
        #         # TODO
        #         return False


class Defense(Player):

    def __init__(self, hockey_world_model):
        super().__init__("defense", hockey_world_model)

    def act(self) -> bool:
        self.walk_around_with_puck() # for now
        return True