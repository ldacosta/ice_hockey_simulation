import math
import random

from geometry.angle import AngleInRadians
from geometry.point import Point
from geometry.vector import Vec2d, NULL_VECTOR
from typing import Tuple, List, Optional

from core.behaviour import Brain
from core.environment import Sensor
from core.environment_state import EnvironmentState
from hockey.behaviour.core.action import HockeyAction
from hockey.core.model import TIME_PER_FRAME
from hockey.core.object_on_ice import ObjectOnIce
from util.base import random_between, stick_length_for_height, INCHES_IN_FOOT
from util.geometry.lines import StraightLine

class Player(ObjectOnIce, Sensor):
    """Hockey Player."""

    # Remember: all speeds are in feet/second.
    MIN_SPEED_MOVING = 14
    MAX_SPEED_MOVING = 22
    MIN_SPEED_SPRINTING = 29
    MAX_SPEED_SPRINTING = 44
    # 'height' is in feet
    MIN_HEIGHT = 6
    MAX_HEIGHT = 7
    # power: serves for puck possession and for shooting
    MIN_POWER = 1
    MAX_POWER = 10
    # speed of puck. In feet/sec. (miles/hour to feet/sec is the transformation).
    SHOT_MIN_SPEED = 80 * 1.4667
    SHOT_MAX_SPEED = 110 * 1.4667
    PASS_SPEED = SHOT_MIN_SPEED / 2
    ## this is how to convert 'power' into speed of shot:
    SHOT_a = (SHOT_MAX_SPEED - SHOT_MIN_SPEED) / (MAX_POWER - MIN_POWER)
    SHOT_b = SHOT_MIN_SPEED - MIN_POWER * SHOT_a
    # time that takes a player to make a pass (or shoot a puck). In seconds.
    TIME_TO_PASS_OR_SHOOT = 0.75

    SHOOT_STRAIGHT_LINE = StraightLine.goes_by(point_1=(MIN_POWER, SHOT_MIN_SPEED), point_2=(MAX_POWER, SHOT_MAX_SPEED))
    # PASS_STRAIGHT_LINE = StraightLine.goes_by(point_1=(MIN_POWER, PASS_MIN_SPEED), point_2=(MAX_POWER, PASS_MAX_SPEED))
    SPRINT_STRAIGHT_LINE = StraightLine.goes_by(point_1=(MIN_POWER, MIN_SPEED_SPRINTING), point_2=(MAX_POWER, MAX_SPEED_SPRINTING))
    SKATE_STRAIGHT_LINE = StraightLine.goes_by(point_1=(MIN_POWER, MIN_SPEED_MOVING), point_2=(MAX_POWER, MAX_SPEED_MOVING))

    @classmethod
    def direction_and_speed_from(cls,
                                 a: HockeyAction,
                                 power: float,
                                 looking_at: Vec2d) -> Optional[Tuple[Vec2d, float]]:
        """
        
        Args:
            a: 
            power: 
            looking_at: 

        Returns:
            On success: A tuple with direction, speed. On returning speed = -1 we indicate that speed should be kept as is.
            On error: None.

        """
        if bool(a & HockeyAction.SHOOT):
            s_line = cls.SHOOT_STRAIGHT_LINE
        elif bool(a & HockeyAction.MOVE):
            s_line = cls.SPRINT_STRAIGHT_LINE
        else:
            return None  # this doesn't look like a speed/direction flag.

        # speed of the action
        if bool(a & HockeyAction.FULL_POWER):
            speed = s_line.apply_to(an_x=power)
        elif bool(a & HockeyAction.HALF_POWER):
            speed = s_line.apply_to(an_x=power/2)
        elif bool(a & HockeyAction.THIRD_OF_POWER):
            speed = s_line.apply_to(an_x=power / 3)
        elif bool(a & HockeyAction.MIN_POWER):
            speed = 1
        elif bool(a & HockeyAction.NO_POWER):
            # I didn't put this to 0 because it leads to numerical errors down the line (on vector speed with norm=0; maybe TODO?)
            speed = 0.01
        elif bool(a & HockeyAction.KEEP_SPEED):
            speed = -1
        else:
            return None  # this doesn't look like a speed/direction flag.
        # which direction should I apply this angle?
        if bool(a & HockeyAction.LEFT):
            direction_multiplier = 1
        elif bool(a & HockeyAction.RIGHT):
            direction_multiplier = -1
        else:
            return None  # this doesn't look like a speed/direction flag.
        # angle (in radians)
        pi_half_over_10 = AngleInRadians.PI_HALF / 10
        if bool(a & HockeyAction.RADIANS_0):
            angle_value = 0
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_1_OVER_10):
            angle_value = pi_half_over_10 * 1
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_2_OVER_10):
            angle_value = pi_half_over_10 * 2
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_3_OVER_10):
            angle_value = pi_half_over_10 * 3
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_4_OVER_10):
            angle_value = pi_half_over_10 * 4
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_5_OVER_10):
            angle_value = pi_half_over_10 * 5
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_6_OVER_10):
            angle_value = pi_half_over_10 * 6
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_7_OVER_10):
            angle_value = pi_half_over_10 * 7
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_8_OVER_10):
            angle_value = pi_half_over_10 * 8
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_9_OVER_10):
            angle_value = pi_half_over_10 * 9
        elif bool(a & HockeyAction.RADIANS_PI_TIMES_10_OVER_10):
            angle_value = pi_half_over_10 * 10
        else:
            return None  # this doesn't look like a speed/direction flag.
        new_vector = looking_at.rotated_radians(
            angle_radians=AngleInRadians(2 * AngleInRadians.PI + direction_multiplier * angle_value))
        return (new_vector, speed)

    def __choose_random_speed__(self) -> float:
        """Returns a speed between 'moving' and 'sprinting' speeds."""
        return random_between(self.moving_speed, self.sprinting_speed)

    def __set_speed_from__(self,
                           an_angle_opt: Optional[AngleInRadians] = None,
                           a_speed_opt: Optional[float] = None) -> bool:
        """Sets speed vector from parameters. Returns True if speed was changed."""
        angle_looking_at = an_angle_opt if (an_angle_opt is not None) else self.speed.angle_with_positive_x_axis()
        current_speed = a_speed_opt if (a_speed_opt is not None) else self.speed.norm()
        if (an_angle_opt is not None) or (a_speed_opt is not None):
            self.speed = Vec2d.from_angle(angle_looking_at).scaled_to_norm(current_speed)
            return True
        else:
            return False

    def __init__(self, prefix_on_id: str, hockey_world_model, brain: Brain):
        ObjectOnIce.__init__(self, prefix_on_id, hockey_world_model,
                         size=3, # feet
                         pos_opt=None)
        Sensor.__init__(self, environment=hockey_world_model)
        self.height = random_between(Player.MIN_HEIGHT, Player.MAX_HEIGHT)
        self.reach = stick_length_for_height(self.height * INCHES_IN_FOOT) / INCHES_IN_FOOT + (self.height / 2) # in feet
        self.moving_speed = random_between(Player.MIN_SPEED_MOVING, Player.MAX_SPEED_MOVING)
        self.sprinting_speed = random_between(Player.MIN_SPEED_SPRINTING, Player.MAX_SPEED_SPRINTING)
        self.power = random_between(Player.MIN_POWER, Player.MAX_POWER)
        self.brain = brain
        self.have_puck = False
        self.reset(to_angle=AngleInRadians.random(), to_speed=0.01) # very slow speed, random direction, to start

    def reset(self, to_speed: Optional[float] = None, to_angle: Optional[AngleInRadians] = None):
        """Resets speed and puck ownership"""

        self.__set_speed_from__(an_angle_opt=to_angle, a_speed_opt=to_speed)
        self.release_puck()
        self.unable_to_play_puck_time = 0.0
        self.last_action = "" # last action performed

    def __str__(self):
        # TODO: complete!
        return \
            "height = %.2f feet, reach = %.2f feet\n" % (self.height, self.reach) + \
            "position: %s\n" % (self.pos) + \
            "speed: %s (norm = %.2f feet/sec)\n" % (self.speed, self.current_speed()) + \
            "Have puck = %s" % (self.have_puck)


    def angle_looking_at(self) -> AngleInRadians:
        return self.speed.angle_with_positive_x_axis()

    def current_speed(self) -> float:
        """In feet per second."""
        return self.speed.norm()

    def vector_looking_at(self) -> Vec2d:
        return self.speed.normalized()

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        # the 'speed' depends on (1) the angle and (2) the actual speed.
        # So I want to update that vector when either change:
        # if (name == "angle_looking_at") or (name == "current_speed"):
        #     if ("angle_looking_at" in self.__dict__) and ("current_speed" in self.__dict__):
        #         self.__dict__["speed"] = self.speed_on_xy()
        #     else:
        #         self.__dict__["speed"] = NULL_VECTOR

    def sense(self) -> EnvironmentState:
        from hockey.behaviour.core.environment_state import EnvironmentState as HockeyEnvironmentState
        return HockeyEnvironmentState(
            me=self,
            puck_owner_opt=self.model.who_has_the_puck(),
            puck_pos_opt=self.model.puck.pos)

    def move_around(self):
        # maybe irrealistic, but it'll do for now:
        self.move_by_bouncing_from_walls()

    def spin_around(self) -> bool:
        """True on success, False otherwise."""
        return self.__set_speed_from__(an_angle_opt=AngleInRadians.random())

    def __vector_me_to_puck_opt__(self) -> Optional[Vec2d]:
        """If I see the puck, this is the vector to it."""
        if not self.can_see_puck():
            # print("Can't calculate a vector to puck because I don't see it") # TODO: put this on a log
            return None
        return self.model.vector_to_puck(self.pos)

    def __pt_in_front_of_me__(self) -> Point:
        """Point that it's right in front of 'my eyes' at a distance of 'reach' """
        as_vector = self.vector_looking_at().normalized() * self.reach
        return Point(self.pos.x + as_vector.x, self.pos.y + as_vector.y)

    def distance_to_puck_opt(self) -> Optional[float]:
        """Distance (in feet) of player that generated this state to the puck."""
        v = self.__vector_me_to_puck_opt__()
        if v is None: # I can't calculate vector to puck: probably I can't see the puck.
            return None
        else:
            return v.norm()


    def can_reach_puck(self) -> bool:
        if self.unable_to_play_puck_time > 0:
            return False
        elif not self.can_see_puck():
            return False # if I can't see the puck, I can't reach it.
        elif self.on_top_of_puck():
            return True # YEAH!
        else:
            d_to_puck = self.distance_to_puck_opt()
            a_to_puck = self.angle_to_puck_opt()
            # print("[my reach = %.2f feet] d to puck = %.2f feet" % (player.reach, d_to_puck))
            return (d_to_puck is not None) and \
                   (round(d_to_puck, 3) <= round(self.reach, 3)) and \
                   (a_to_puck is not None) and \
                   ((a_to_puck <= AngleInRadians(AngleInRadians.PI_HALF)) or
                    (a_to_puck >= AngleInRadians(AngleInRadians.THREE_HALFS_OF_PI)))

    def angle_to_puck_opt(self) -> Optional[AngleInRadians]:
        """
        Angle to puck, defined in [0, 2Pi]. If puck is at the right of the vector
        defined by a straight line right in front of me, then this angle will be in [Pi, 2Pi]
        If it's at my left, the angle is in [0,Pi]
        """
        angle = self.model.angle_to_puck(self.pos, self.vector_looking_at())
        if angle <= AngleInRadians(AngleInRadians.PI_HALF) or \
                        angle >= AngleInRadians(AngleInRadians.THREE_HALFS_OF_PI):
            return angle
        else:
            return None

    def angles_to_goal(self) -> Tuple[Optional[AngleInRadians], Optional[AngleInRadians]]:
        """
        Returns 2 vectors: 1 for each vertical post.
        Angles are defined in [0, 2Pi]. If puck is at the right of the vector
        defined by a straight line right in front of me, then this angle will be in [Pi, 2Pi]
        If it's at my left, the angle is in [0,Pi]
        """
        def angle_visible(an_angle: AngleInRadians) -> bool:
            return (an_angle.value <= AngleInRadians.PI_HALF) or (an_angle.value >= AngleInRadians.THREE_HALFS_OF_PI)
        a1, a2 = self.model.angles_to_goal(a_pos=self.pos, looking_at=self.vector_looking_at())
        if not angle_visible(a1):
            r1 = None
        else:
            r1 = a1
        if not angle_visible(a2):
            r2 = None
        else:
            r2 = a2
        return (r1, r2)
        # one_post = Point(x=self.model.goal_position[0], y=self.model.goal_position[1][0])
        # other_post = Point(x=self.model.goal_position[0], y=self.model.goal_position[1][1])
        # v_to_one_post = Vec2d.from_to(from_pt=self.pos, to_pt=one_post)
        # v_to_other_post = Vec2d.from_to(from_pt=self.pos, to_pt=other_post)
        # v_front_of_me = self.vector_looking_at()
        # return (v_front_of_me.angle_to(v_to_one_post), v_front_of_me.angle_to(v_to_other_post))

    def min_angle_to_goal_opt(self) -> Optional[AngleInRadians]:
        """TODO: """
        # TODO: this thing returns None's!
        a1, a2 = self.angles_to_goal()
        if a1 is None and a2 is None:
            return None
        else:
            if a1 is None:
                return a2
            elif a2 is None:
                return a1
            else:
                return min(self.angles_to_goal())

    def on_top_of_puck(self) -> bool:
        """True if the player is on top of puck."""
        return self.pos == self.model.puck.pos

    def can_see_puck(self) -> bool:
        if self.on_top_of_puck():
            return True
        else:
            angle_to_puck = self.angle_to_puck_opt()
            return (angle_to_puck is not None) and \
                   ((angle_to_puck <= AngleInRadians(AngleInRadians.PI_HALF)) or
                    (angle_to_puck >= AngleInRadians(AngleInRadians.THREE_HALFS_OF_PI)))

    def can_see_goal_posts(self) -> Tuple[bool, bool]:
        """Can I see the FRONT of the goal posts?"""
        if self.pos.x > self.model.goal_position[0]: # I am behind the goal
            return (False, False)
        a1, a2 = self.angles_to_goal()
        return (a1 is not None, a2 is not None)

    def distance_to_goal_posts(self) -> Tuple[Optional[float], Optional[float]]:
        """Distance, in feet, to both goal posts"""
        d1, d2 = self.model.distance_to_goal_posts(self.pos)
        can_see_post_1, can_see_post_2 = self.can_see_goal_posts()
        return (d1 if can_see_post_1 else None, d2 if can_see_post_2 else None)

    def can_see_goal(self) -> bool:
        """Can I see the front of the goal?"""
        can_see_post_1, can_see_post_2 = self.can_see_goal_posts()
        return can_see_post_1 or can_see_post_2

    def __wander_around__(self):
        self.move_around()
        if random.random() <= 0.10:
            self.spin_around()

    def grab_puck(self) -> bool:
        if (not self.have_puck) and self.can_reach_puck():
            self.model.puck_request_by(self)
        return self.have_puck

    def align_with_puck(self) -> bool:
        """Sets the speed's angle such that it aligns with puck."""
        if (self.on_top_of_puck()):
            return True
        self.speed = self.model.vector_to_puck(self.pos).scaled_to_norm(self.speed.norm())
        return True

    def __parse_action__(self, a: HockeyAction) -> bool:
        """
        
        Args:
            a: 

        Returns:
            True if the action was successfully taken. False otherwise.

        """
        action_taken = True
        do_move = True # unless otherwise stated, after taking the action I have to move
        # if a == HockeyAction.GRAB_PUCK:
        #     action_taken = self.grab_puck()
        #     if action_taken:
        #         self.__set_speed_from__(a_speed_opt=self.current_speed() / 2) # grabbing the puck slows me down
        #     self.last_action = "Grab puck"
        if a == HockeyAction.ALIGN_WITH_PUCK:
            action_taken = self.align_with_puck()
            self.last_action = "Align with puck"
        elif bool(a & HockeyAction.MOVE):
            r = Player.direction_and_speed_from(a, power=self.power, looking_at=self.vector_looking_at())
            assert r is not None # see the condition above
            direction, speed = r
            old_speed = self.speed
            self.__set_speed_from__(an_angle_opt=direction.angle_with_positive_x_axis(),
                                    a_speed_opt=speed if speed >= 0 else None)
            # mini sanity-check
            la_norm =  self.vector_looking_at()
            dir_norm = direction.normalized()
            if not ((abs(la_norm.x - dir_norm.x) <= 1e-3) and (abs(la_norm.y - dir_norm.y) <= 1e-3)):
                # redo, for debugging purposes
                self.speed = old_speed
                self.__set_speed_from__(an_angle_opt=direction.angle_with_positive_x_axis(),
                                        a_speed_opt=speed if speed >= 0 else None)

            assert (abs(la_norm.x - dir_norm.x) <= 1e-3) and (abs(la_norm.y - dir_norm.y) <= 1e-3), \
                "looking at: %s, direction: %s" % (self.vector_looking_at().normalized(), direction.normalized())
            self.last_action = "Move => speed = %.2f feet/sec, direction = %s, so I am going %s" % (self.current_speed(), self.angle_looking_at(), self.speed)
        elif bool(a & HockeyAction.SHOOT):
            r = Player.direction_and_speed_from(a, power=self.power, looking_at=self.vector_looking_at())
            assert r is not None # see the condition above
            direction, speed = r
            assert speed > 0
            self.last_action = "send puck, speed = %.2f feet/sec, direction = %s" % (speed, direction)
            action_taken = self.__send_puck__(puck_speed_vector=direction, speed_multiplier=speed)
            self.__set_speed_from__(a_speed_opt=self.current_speed()/10) # shooting drastically slows me down
        else:
            action_taken = False
            raise RuntimeError("Player does not know how to interpret action %s" % (a))
        # wrap-up:
        if do_move:
            self.move_by_bouncing_from_walls()
        if self.have_puck:
            self.model.space.place_agent(self.model.puck, self.pos)
        if not action_taken:
            self.last_action = "[FAILED] " + self.last_action
        # if (a == HockeyAction.GRAB_PUCK) and action_taken:
        #     assert self.have_puck
        # Sanity check: whatever I do. at the end sanity should prevail:
        self.__sanity_check_or_explode__()
        # grab the puck if you're REALLY close to it!
        if self.can_reach_puck():
            action_taken = self.grab_puck()
            print("GRAB PUCK BY PROXIMITY => succeeded? -> %s" % (action_taken))
            assert action_taken
            assert self.have_puck

        return action_taken

    def __sanity_check_or_explode__(self):
        """Properties that have to hold at all moments"""

        # vector looking at is normalized
        assert abs(self.vector_looking_at().norm() - 1.0) < 1e-3, \
            "self.vector_looking_at().norm() = %.2f" % self.vector_looking_at().norm()
        #
        if self.current_speed() != 0:
            assert self.speed.normalized() == self.vector_looking_at(), \
                "angle looking at = %s, current speed = %.2f, speed = %s, looking at = %s" % \
                (self.angle_looking_at(), self.current_speed(), self.speed.normalized(), self.vector_looking_at())

    def apply_actions(self, actions: List[HockeyAction]) -> bool:
        return [self.__parse_action__(an_action) for an_action in actions][-1]

    def act(self) -> bool:
        return self.apply_actions(self.brain.propose_actions(the_state=self.sense())) #, action_handler=self.__parse_action__)

    def turn_left(self):
        self.__set_speed_from__(an_angle_opt=AngleInRadians(self.angle_looking_at().value + AngleInRadians.PI_HALF))

    def turn_right(self):
        self.__set_speed_from__(an_angle_opt=AngleInRadians(self.angle_looking_at().value - AngleInRadians.PI_HALF))

    def is_puck_owned_by_my_team(self) -> bool:
        current_owner = self.model.who_has_the_puck()
        if current_owner is None:
            return False
        else:
            return type(self) == type(current_owner)

    def first_visible_goal_point(self) -> Optional[Point]:
        return self.model.first_visible_goal_point_from(a_position=self.pos)

    def release_puck(self):
        if self.have_puck:
            self.have_puck = False
            self.model.puck.set_free()
            self.model.puck.speed = Vec2d(0,0)

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

    def update_unable_time(self):
        self.unable_to_play_puck_time = max(0, self.unable_to_play_puck_time - TIME_PER_FRAME)

    def step(self):
        self.update_unable_time()
        self.act()
