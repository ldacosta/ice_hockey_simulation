
import math
from typing import Optional
from geometry.point import Point
from geometry.vector import Vec2d, angle_between
from geometry.angle import AngleInRadians, rotatePoint
from core.environment_state import EnvironmentState as CoreEnvironmentState
from hockey.core.player.base import Player

class EnvironmentState(CoreEnvironmentState):

    def __init__(self, me: Player, puck_owner_opt: Optional[Player], puck_pos_opt: Optional[Point]):
        CoreEnvironmentState.__init__(self, my_id=me.unique_id)
        self.me = me
        self.puck_owner_opt = puck_owner_opt
        self.puck_pos_opt = puck_pos_opt

    def have_puck(self) -> bool:
        if self.puck_owner_opt is None:
            return False
        return self.id == self.puck_owner_opt.unique_id

    def my_team_has_puck(self) -> bool:
        if self.puck_owner_opt is None:
            return False
        return type(self.puck_owner_opt) == type(self.me)

    def __vector_me_to_puck__(self) -> Vec2d:
        if self.puck_pos_opt is None:
            raise RuntimeError("Can't calculate a vector to puck because I don't see it")
        return Vec2d.from_to(from_pt=self.me.pos, to_pt=self.puck_pos_opt)

    def can_I_reach_puck(self) -> bool:
        if self.me.unable_to_play_puck_time > 0:
            return False
        else:
            vector_me_to_puck = self.__vector_me_to_puck__()
            if vector_me_to_puck.is_zero(): # I am standing ON TOP OF PUCK!!
                return True
            elif vector_me_to_puck.norm() > self.me.reach: # puck too far
                return False
            else: # is it in front of me?
                # what IS the point "just in front" of me?
                p_alpha = self.me.__pt_in_front_of_me__()
                # find the 2 points that make the diameter of the semi-circle in front of me:
                p_a = rotatePoint(centerPoint=self.me.pos, point=p_alpha, angle=AngleInRadians(value=math.pi / 2))
                p_b = rotatePoint(centerPoint=self.me.pos, point=p_alpha, angle=AngleInRadians.from_minus_pi_to_plus_pi(value=-math.pi / 2))
                # vector of the radius:
                v_radius = Vec2d.from_to(from_pt=p_a, to_pt=p_b) # Vector2D(pt_from=p_a, pt_to=p_b)
                # ok, finally:
                the_angle = angle_between(v1 = v_radius, v2 = vector_me_to_puck)
                return the_angle.value <= math.pi

