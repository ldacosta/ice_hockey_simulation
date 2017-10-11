import math
import random

import numpy as np
from geometry.angle import AngleInRadians, rotatePoint
from geometry.point import Point
from geometry.vector import Vec2d, angle_between
from typing import Tuple, List

from core.behaviour import Brain
from core.environment import Sensor
from core.environment_state import EnvironmentState
from hockey.behaviour.core.action import HockeyAction
from hockey.core.model import TIME_PER_FRAME
from hockey.core.object_on_ice import ObjectOnIce
from util.base import normalize_to


class Player(ObjectOnIce, Sensor):
    """Hockey Player."""

    # Remember: all speeds are in feet/second.
    MIN_SPEED_MOVING = 14
    MAX_SPEED_MOVING = 22
    MIN_SPEED_SPRINTING = 29
    MAX_SPEED_SPRINTING = 44
    #
    MIN_REACH = 3
    MAX_REACH = 6
    # power: serves for puck possession and for shooting
    MIN_POWER = 1
    MAX_POWER = 10
    # time that takes a player to make a pass (or shoot a puck). In seconds.
    TIME_TO_PASS_OR_SHOOT = 0.75

    def __choose_random_speed__(self) -> float:
        """Returns a speed between 'moving' and 'sprinting' speeds."""
        return normalize_to(
            random.random(),
            new_min=self.moving_speed, new_max=self.sprinting_speed,
            old_min=0, old_max=1)


    def __init__(self, prefix_on_id: str, hockey_world_model, brain: Brain):
        self.angle_looking_at = AngleInRadians.random()
        self.moving_speed = normalize_to(
            random.random(),
            new_min = Player.MIN_SPEED_MOVING, new_max = Player.MAX_SPEED_MOVING,
            old_min = 0, old_max = 1)
        self.sprinting_speed = normalize_to(
            random.random(),
            new_min = Player.MIN_SPEED_SPRINTING, new_max = Player.MAX_SPEED_SPRINTING,
            old_min = 0, old_max = 1)
        self.current_speed = self.__choose_random_speed__()
        # power: serves for puck possession and for shooting
        self.power = normalize_to(
            random.random(),
            new_min = Player.MIN_POWER, new_max = Player.MAX_POWER,
            old_min = 0, old_max = 1)
        self.brain = brain
        ObjectOnIce.__init__(self, prefix_on_id, hockey_world_model,
                         size=3, # feet
                         pos_opt=None,
                         speed_opt=self.speed_on_xy())
        Sensor.__init__(self, environment=hockey_world_model)
        self.reach = normalize_to(
            random.random(),
            new_min = Player.MIN_REACH, new_max = Player.MAX_REACH,
            old_min = 0, old_max = 1)
        self.have_puck = False
        self.unable_to_play_puck_time = 0

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def sense(self) -> EnvironmentState:
        from hockey.behaviour.core.environment_state import EnvironmentState as HockeyEnvironmentState

        return HockeyEnvironmentState(
            me=self,
            puck_owner_opt=self.model.who_has_the_puck(),
            puck_pos_opt=self.model.puck.pos)

    def speed_on_xy(self) -> Vec2d:
        return self.vector_looking_at() * self.current_speed

    def move_around(self):
        # maybe irrealistic, but it'll do for now:
        self.move_by_bouncing_from_walls()

    def spin_around(self):
        self.angle_looking_at.randomly_mutate()
        self.speed = self.speed_on_xy()


    def __vector_me_to_puck__(self) -> Vec2d:
        return Vec2d.from_to(from_pt=self.pos, to_pt=self.model.puck.pos)

    def __pt_in_front_of_me__(self) -> Tuple[float, float]:
        p0 = (self.pos[0] + self.reach, self.pos[1])  # looking at angle = 0
        p1 = rotatePoint(centerPoint=self.pos, point=p0, angle=self.angle_looking_at)
        return p1

    def can_reach_puck(self) -> bool:
        if self.unable_to_play_puck_time > 0:
            return False
        else:
            vector_me_to_puck = self.__vector_me_to_puck__()
            if vector_me_to_puck.is_zero(): # I am standing ON TOP OF PUCK!!
                return True
            elif vector_me_to_puck.norm() > self.reach: # puck too far
                return False
            else: # is it in front of me?
                # what IS the point "just in front" of me?
                p_alpha = self.__pt_in_front_of_me__()
                # find the 2 points that make the diameter of the semi-circle in front of me:
                p_a = rotatePoint(centerPoint=self.pos, point=p_alpha, angle=AngleInRadians(value=math.pi / 2))
                p_b = rotatePoint(centerPoint=self.pos, point=p_alpha, angle=AngleInRadians.from_minus_pi_to_plus_pi(value=-math.pi / 2))
                # vector of the radius:
                v_radius = Vec2d.from_to(from_pt=p_a, to_pt=p_b) # Vector2D(pt_from=p_a, pt_to=p_b)
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
        return angle_between(v1=v_me_to_puck, v2=v_front_of_me) < AngleInRadians.PI_HALF
        # return (angle_between(v1=v_me_to_puck, v2=v_front_of_me) < AngleInRadians.PI_HALF) or \
        #        (angle_between(v1=v_front_of_me, v2=v_me_to_puck) < AngleInRadians.PI_HALF)

    def __wander_around__(self):
        self.move_around()
        if random.random() <= 0.10:
            self.spin_around()

    def __parse_action__(self, a: HockeyAction) -> bool:
        if a == HockeyAction.MOVE_RANDOM_SPEED:
            self.current_speed = self.__choose_random_speed__()
            self.move_by_bouncing_from_walls()
        elif a == HockeyAction.SPRINT:
            self.current_speed = self.sprinting_speed
            self.move_by_bouncing_from_walls()
        elif a == HockeyAction.SKATE_CALMLY:
            self.current_speed = self.moving_speed
            self.move_by_bouncing_from_walls()
        elif a == HockeyAction.SPIN_RANDOMLY:
            self.spin_around()
        elif a == HockeyAction.NOOP:
            pass # doing nothing alright!
        elif a == HockeyAction.SHOOT:
            # TODO: 'towards the goal', unless I don't see it
            self.shoot_puck(direction=Vec2d(tuple(np.random.normal(loc=0.0, scale=5.0, size=2))))
            self.move_around()
        elif a == HockeyAction.PASS:
            pass  # TODO
        elif a == HockeyAction.CHASE_PUCK:
            self.chase_puck(only_when_my_team_doesnt_have_it=True) # TODO: verify flag
        elif a == HockeyAction.GRAB_PUCK:
            self.model.puck_request_by(self)
            if (self.have_puck):
                print("[%s] I JUST TOOK the puck!" % (self.unique_id))
        else:
            raise RuntimeError("Player does not know how to interpret action %s" % (a))
        # wrap-up:
        if self.have_puck:
            self.model.space.place_agent(self.model.puck, self.pos)
        return True

    def apply_actions(self, actions: List[HockeyAction], action_handler) -> bool:
        actions = self.brain.propose_actions(the_state=self.sense())
        return [action_handler(an_action) for an_action in actions][-1]

    def act(self) -> bool:
        return self.apply_actions(self.brain.propose_actions(the_state=self.sense()), action_handler=self.__parse_action__)

    def turn_left(self):
        self.angle_looking_at += (math.pi / 2)

    def turn_right(self):
        self.angle_looking_at -= (math.pi / 2)

    def is_puck_owned_by_my_team(self) -> bool:
        current_owner = self.model.who_has_the_puck()
        if current_owner is None:
            return False
        else:
            return type(self) == type(current_owner)

    def chase_puck(self, only_when_my_team_doesnt_have_it: bool) -> bool:
        """Skate as fast as possible in the direction of the puck."""
        if self.can_see_puck():
            print("[chase_puck][%s] I can see puck. Going towards it now" % (self.unique_id))
            self.current_speed = self.sprinting_speed # let's go FAST!
            # Turn towards puck, if needed
            angle_to_puck = self.angle_to_puck()
            if abs(angle_to_puck.value) >= math.pi / 10:  # TODO: do something "better"
                print(" ====> I am looking at angle %s, angle to puck is %s, so I am turning to the sum of both" % (self.angle_looking_at, angle_to_puck))
                self.angle_looking_at += angle_to_puck
            self.speed = self.speed_on_xy()
        else:
            print("[chase_puck][%s] I can't see puck. " % (self.unique_id))
            # I can neither reach or even see the puck
            if random.random() < 0.5:
                self.turn_left()
            else:
                self.turn_right()
        self.move_by_bouncing_from_walls()
        return True

    def release_puck(self):
        if self.have_puck:
            self.have_puck = False
            self.model.puck.is_taken = False

    def __send_puck__(self, puck_speed_vector: Vec2d, speed_multiplier: float):
        if self.have_puck:
            speed_multiplier = max([0, speed_multiplier])
            self.release_puck()
            self.model.puck.speed = puck_speed_vector.normalized() * speed_multiplier
            self.unable_to_play_puck_time = self.TIME_TO_PASS_OR_SHOOT

    def shoot_puck(self, direction: Vec2d):
        self.__send_puck__(puck_speed_vector=direction, speed_multiplier=self.current_speed * 2) # TODO: vary speed

    def pass_puck(self, this_position: Point):
        direction = Vec2d.from_to(self.pos, this_position)
        self.__send_puck__(puck_speed_vector=direction, speed_multiplier=self.current_speed * 2) # TODO: vary speed

    def vector_looking_at(self) -> Vec2d:
        return Vec2d.from_angle(self.angle_looking_at)

    def step(self):
        self.unable_to_play_puck_time = max(0, self.unable_to_play_puck_time - TIME_PER_FRAME)
        self.act()