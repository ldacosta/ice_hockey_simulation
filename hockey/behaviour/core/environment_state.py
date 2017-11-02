
import math
from typing import Optional
from geometry.point import Point
from geometry.vector import Vec2d, angle_between
from geometry.angle import AngleInRadians, rotatePoint
from core.environment_state import EnvironmentState as CoreEnvironmentState
from hockey.core.player.base import Player
from hockey.core.player.forward import Forward

class EnvironmentState(CoreEnvironmentState):

    def __init__(self, me: Player, puck_owner_opt: Optional[Player], puck_pos_opt: Optional[Point]):
        CoreEnvironmentState.__init__(self, my_id=me.unique_id)
        self.me = me
        self.puck_owner_opt = puck_owner_opt
        self.puck_pos_opt = puck_pos_opt
        self.attacking = (type(me) == Forward)

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
        return self.me.can_reach_puck()

    def distance_to_puck(self) -> float:
        """Distance (in feet) of player that generated this state to the puck."""
        return self.__vector_me_to_puck__().norm()

    def distance_to_goal(self) -> float:
        """Distance (in feet) of player that generated this state to the goal."""
        return self.me.model.distance_to_goal(self.me.pos)
