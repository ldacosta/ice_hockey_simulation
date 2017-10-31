import math
import random

import numpy as np
from geometry.angle import AngleInRadians, rotatePoint
from geometry.point import Point
from geometry.vector import Vec2d, angle_between
from typing import Tuple, List, Optional

from core.behaviour import Brain
from core.environment import Sensor
from core.environment_state import EnvironmentState
from hockey.behaviour.core.action import HockeyAction
from hockey.core.model import TIME_PER_FRAME
from hockey.core.object_on_ice import ObjectOnIce
from util.base import random_between, stick_length_for_height, INCHES_IN_FOOT

class Player(ObjectOnIce, Sensor):
    """Hockey Player."""

    # Remember: all speeds are in feet/second.
    MIN_SPEED_MOVING = 14
    MAX_SPEED_MOVING = 22
    MIN_SPEED_SPRINTING = 29
    MAX_SPEED_SPRINTING = 44
    # 'height' is in feet
    MIN_HEIGHT = 4
    MAX_HEIGHT = 7
    # power: serves for puck possession and for shooting
    MIN_POWER = 1
    MAX_POWER = 10
    # speed of puck. In feet/sec. (miles / hour to feet / sec is the transformation).
    SHOT_MIN_SPEED = 80 * 1.4667
    SHOT_MAX_SPEED = 110 * 1.4667
    PASS_SPEED = SHOT_MIN_SPEED / 2
    ## this is how to convert 'power' into speed of shot:
    SHOT_a = (SHOT_MAX_SPEED - SHOT_MIN_SPEED) / (MAX_POWER - MIN_POWER)
    SHOT_b = SHOT_MIN_SPEED - MIN_POWER * SHOT_a
    # time that takes a player to make a pass (or shoot a puck). In seconds.
    TIME_TO_PASS_OR_SHOOT = 0.75

    def __choose_random_speed__(self) -> float:
        """Returns a speed between 'moving' and 'sprinting' speeds."""
        return random_between(self.moving_speed, self.sprinting_speed)


    def __init__(self, prefix_on_id: str, hockey_world_model, brain: Brain):
        self.height = random_between(Player.MIN_HEIGHT, Player.MAX_HEIGHT)
        self.reach = stick_length_for_height(self.height * INCHES_IN_FOOT) / INCHES_IN_FOOT # in feet
        self.angle_looking_at = AngleInRadians.random()
        self.moving_speed = random_between(Player.MIN_SPEED_MOVING, Player.MAX_SPEED_MOVING)
        self.sprinting_speed = random_between(Player.MIN_SPEED_SPRINTING, Player.MAX_SPEED_SPRINTING)
        self.current_speed = self.__choose_random_speed__()
        self.power = random_between(Player.MIN_POWER, Player.MAX_POWER)
        self.brain = brain
        ObjectOnIce.__init__(self, prefix_on_id, hockey_world_model,
                         size=3, # feet
                         pos_opt=None,
                         speed_opt=self.speed_on_xy())
        Sensor.__init__(self, environment=hockey_world_model)
        self.have_puck = False
        self.unable_to_play_puck_time = 0.0
        self.speed = self.speed_on_xy()
        self.last_action = "" # last action performed

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

    def __pt_in_front_of_me__(self) -> Point:
        """Point that it's right in front of 'my eyes' at a distance of 'reach' """
        as_vector = self.vector_looking_at().normalized() * self.reach
        return Point(self.pos.x + as_vector.x, self.pos.y + as_vector.y)

    def can_reach_puck(self) -> bool:
        if self.unable_to_play_puck_time > 0:
            return False
        elif not self.can_see_puck():
            return False # if I can't see the puck, I can't reach it.
        else:
            d_to_puck = self.model.distance_to_puck(self.pos)
            # print("[my reach = %.2f feet] d to puck = %.2f feet" % (player.reach, d_to_puck))
            return (round(d_to_puck, 3) <= round(self.reach, 3)) and \
                   (self.angle_to_puck().value <= AngleInRadians.PI_HALF)

    def angle_to_puck(self) -> AngleInRadians:
        v_me_to_puck = self.__vector_me_to_puck__()
        v_front_of_me = self.vector_looking_at()
        return angle_between(v1=v_me_to_puck, v2=v_front_of_me)

    def angles_to_goal(self) -> Tuple[AngleInRadians, AngleInRadians]:
        """Returns 2 vectors: 1 for each vertical post."""
        one_post = Point(x=self.model.goal_position[0], y=self.model.goal_position[1][0])
        other_post = Point(x=self.model.goal_position[0], y=self.model.goal_position[1][1])
        v_to_one_post = Vec2d.from_to(from_pt=self.pos, to_pt=one_post)
        v_to_other_post = Vec2d.from_to(from_pt=self.pos, to_pt=other_post)
        v_front_of_me = self.vector_looking_at()
        return (angle_between(v1=v_to_one_post, v2=v_front_of_me), angle_between(v1=v_to_one_post, v2=v_to_other_post))

    def min_angle_to_goal(self) -> AngleInRadians:
        return min(self.angles_to_goal())

    def on_top_of_puck(self) -> bool:
        """True if the player is on top of puck."""
        return self.pos == self.model.puck.pos

    def can_see_puck(self) -> bool:
        if self.on_top_of_puck():
            return True
        else:
            return self.angle_to_puck().value <= AngleInRadians.PI_HALF

    def can_see_goal(self) -> bool:
        angle_to_one_post, angle_to_other_post = self.angles_to_goal()
        return (angle_to_one_post.value <= AngleInRadians.PI_HALF) or \
               (angle_to_other_post.value <= AngleInRadians.PI_HALF)

    def __wander_around__(self):
        self.move_around()
        if random.random() <= 0.10:
            self.spin_around()

    def grab_puck(self) -> bool:
        if (not self.have_puck) and self.can_reach_puck():
            self.model.puck_request_by(self)
        return self.have_puck

    def __parse_action__(self, a: HockeyAction) -> bool:
        """
        
        Args:
            a: 

        Returns:
            True if the action was successfully taken. False otherwise.

        """
        action_taken = True
        if a == HockeyAction.MOVE_RANDOM_SPEED:
            self.current_speed = self.__choose_random_speed__()
            self.speed = self.speed_on_xy()
            self.move_by_bouncing_from_walls()
            self.last_action = "Move at random (%.2f feet/sec.) speed" % self.current_speed
        elif a == HockeyAction.SPRINT:
            self.current_speed = self.sprinting_speed
            self.speed = self.speed_on_xy()
            self.move_by_bouncing_from_walls()
            self.last_action = "Move at SPRINTING (%.2f feet/sec.) speed" % self.current_speed
        elif a == HockeyAction.SKATE_CALMLY:
            self.current_speed = self.moving_speed
            self.speed = self.speed_on_xy()
            self.move_by_bouncing_from_walls()
            self.last_action = "Skate calmly: (%.2f feet/sec.) speed" % self.current_speed
        elif a == HockeyAction.SPIN_RANDOMLY:
            self.spin_around()
            self.last_action = "Spin randomly"
        elif a == HockeyAction.NOOP:
            self.last_action = "NOOP"
            pass # doing nothing alright!
        elif a == HockeyAction.SHOOT:
            # _should_ be taken care of by specific kind of player -
            # but if it gets here,, let's throw the puck to a random place.
            self.shoot_puck(direction=Vec2d(tuple(np.random.normal(loc=0.0, scale=5.0, size=2))))
            self.move_around()
            self.last_action = "Generic SHOOT [are we sure this is OK????]"
        elif a == HockeyAction.PASS:
            self.last_action = "Generic PASS [are we sure this is OK????]"
            pass  # TODO
        elif a == HockeyAction.CHASE_PUCK:
            self.chase_puck(only_when_my_team_doesnt_have_it=True) # TODO: verify flag
            self.last_action = "Chase puck"
        elif a == HockeyAction.GRAB_PUCK:
            action_taken = self.grab_puck()
            if action_taken:
                print(" *************************** SUCCESSFUL Grab puck")
                self.last_action = "SUCCESSFUL Grab puck"
            else:
                # print(" *************************** UN-SUCCESSFUL Grab puck")
                self.last_action = "UNSUCCESSFUL Grab puck"
        else:
            action_taken = False
            raise RuntimeError("Player does not know how to interpret action %s" % (a))
        # wrap-up:
        if self.have_puck:
            self.model.space.place_agent(self.model.puck, self.pos)
        return action_taken

    # def apply_actions(self, actions: List[HockeyAction], action_handler = __parse_action__) -> bool:
    #     actions = self.brain.propose_actions(the_state=self.sense())
    #     return [action_handler(an_action) for an_action in actions][-1]

    def apply_actions(self, actions: List[HockeyAction]) -> bool:
        return [self.__parse_action__(an_action) for an_action in actions][-1]

    def act(self) -> bool:
        return self.apply_actions(self.brain.propose_actions(the_state=self.sense())) #, action_handler=self.__parse_action__)

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

    def first_visible_goal_point(self) -> Optional[Point]:
        return self.model.first_visible_goal_point_from(a_position=self.pos)

    def chase_puck(self, only_when_my_team_doesnt_have_it: bool) -> bool:
        """Skate as fast as possible in the direction of the puck."""
        if self.can_see_puck():
            # print("[chase_puck][%s] I can see puck. Going towards it now" % (self.unique_id))
            self.current_speed = self.sprinting_speed # let's go FAST!
            # Turn towards puck, if needed
            angle_to_puck = self.angle_to_puck()
            if abs(angle_to_puck.value) >= math.pi / 10:  # TODO: do something "better"
                # print(" ====> I am looking at angle %s, angle to puck is %s, so I am turning to the sum of both" % (self.angle_looking_at, angle_to_puck))
                self.angle_looking_at += angle_to_puck
            self.speed = self.speed_on_xy()
        else:
            # print("[chase_puck][%s] I can't see puck. " % (self.unique_id))
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
            self.model.puck.set_free()

    def __send_puck__(self, puck_speed_vector: Vec2d, speed_multiplier: float) -> bool:
        if self.have_puck:
            speed_multiplier = max([0, speed_multiplier])
            self.release_puck()
            self.model.puck.speed = puck_speed_vector.normalized() * speed_multiplier
            self.unable_to_play_puck_time = self.TIME_TO_PASS_OR_SHOOT
            return True
        return False

    def shoot_puck(self, direction: Vec2d) -> bool:
        speed = Player.SHOT_a * self.power + Player.SHOT_b
        return self.__send_puck__(puck_speed_vector=direction, speed_multiplier=speed)

    def pass_puck(self, this_position: Point) -> bool:
        direction = Vec2d.from_to(self.pos, this_position)
        return self.__send_puck__(puck_speed_vector=direction, speed_multiplier=Player.PASS_SPEED) # TODO: vary speed? Maybe?

    def vector_looking_at(self) -> Vec2d:
        return Vec2d.from_angle(self.angle_looking_at)

    def update_unable_time(self):
        self.unable_to_play_puck_time = max(0, self.unable_to_play_puck_time - TIME_PER_FRAME)

    def step(self):
        self.update_unable_time()
        self.act()
