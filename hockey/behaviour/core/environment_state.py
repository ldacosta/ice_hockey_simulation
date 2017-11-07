
from typing import Optional, Tuple
from geometry.point import Point
from geometry.angle import AngleInRadians
from core.environment_state import EnvironmentState as CoreEnvironmentState
from hockey.core.player.base import Player
from hockey.core.player.forward import Forward

class EnvironmentState(CoreEnvironmentState):
    """
    All things that an agent can sense from the environment.
    Putting all attributes as parameter-less functions that can then be called from,
    eg, bitstring_environment_state
    """

    def __init__(self, me: Player, puck_owner_opt: Optional[Player], puck_pos_opt: Optional[Point]):
        CoreEnvironmentState.__init__(self, my_id=me.unique_id)
        self.me = me
        self.puck_owner_opt = puck_owner_opt
        self.puck_pos_opt = puck_pos_opt

    def attacking(self) -> bool:
        return (type(self.me) == Forward)

    def have_puck(self) -> bool:
        if self.puck_owner_opt is None:
            return False
        return self.id == self.puck_owner_opt.unique_id

    def can_see_puck(self) -> bool:
        return self.me.can_see_puck()

    def my_team_has_puck(self) -> bool:
        if self.puck_owner_opt is None:
            return False
        return type(self.puck_owner_opt) == type(self.me)

    def can_I_reach_puck(self) -> bool:
        return self.me.can_reach_puck()

    # ********************************************************************
    # Puck

    def __puck_closer_than__(self, n_feet: float) -> bool:
        dist_to_puck_opt = self.me.distance_to_puck_opt()
        return self.me.can_see_puck() and (dist_to_puck_opt is not None) and (dist_to_puck_opt <= n_feet)

    def puck_closer_than_10_feet(self) -> bool:
        return self.__puck_closer_than__(10)

    def puck_closer_than_20_feet(self) -> bool:
        return self.__puck_closer_than__(20)

    def puck_closer_than_30_feet(self) -> bool:
        return self.__puck_closer_than__(30)

    def puck_closer_than_40_feet(self) -> bool:
        return self.__puck_closer_than__(40)

    def puck_closer_than_50_feet(self) -> bool:
        return self.__puck_closer_than__(50)

    def puck_closer_than_60_feet(self) -> bool:
        return self.__puck_closer_than__(60)

    def puck_to_my_right(self) -> bool:
        """Can I See the puck to my right?"""
        angle_to_puck = self.me.angle_to_puck_opt()
        return ((angle_to_puck is not None) and (angle_to_puck.value >= AngleInRadians.THREE_HALFS_OF_PI))

    def puck_to_my_left(self) -> bool:
        """Can I See the puck to my left?"""
        return self.can_see_puck() and (not self.puck_to_my_right())

    # angles: this are defined here as the minimum angle between 2 vectors (eg, 20 degrees to the left or to the right)
    def __angle_to_puck__(self) -> Optional[float]:
        """Irrespective of which side ('right' or 'left')"""
        a = self.me.angle_to_puck_opt()
        if a is None:
            return None
        elif a.value <= AngleInRadians.PI_HALF:
            return a.value
        else:
            return AngleInRadians.PI * 2 - a.value

    def __angle_to_puck_less_than__(self, angle_value: float) -> bool:
        a = self.__angle_to_puck__()
        return a is not None and a <= angle_value

    def angle_to_puck_less_than_pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=AngleInRadians.PI / 10)

    def angle_to_puck_less_than_2pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=2*AngleInRadians.PI / 10)

    def angle_to_puck_less_than_3pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=3*AngleInRadians.PI / 10)

    def angle_to_puck_less_than_4pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=4*AngleInRadians.PI / 10)

    def angle_to_puck_less_than_5pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=5*AngleInRadians.PI / 10)

    def angle_to_puck_less_than_6pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=6*AngleInRadians.PI / 10)

    def angle_to_puck_less_than_7pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=7*AngleInRadians.PI / 10)

    def angle_to_puck_less_than_8pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=8*AngleInRadians.PI / 10)

    def angle_to_puck_less_than_9pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=9*AngleInRadians.PI / 10)

    def angle_to_puck_less_than_10pi_over_10(self) -> bool:
        return self.__angle_to_puck_less_than__(angle_value=AngleInRadians.PI)

    # ********************************************************************
    # Goal

    def can_see_goal(self) -> bool:
        return self.me.can_see_goal()

    def can_see_goal_post_1(self) -> bool:
        return self.me.can_see_goal_posts()[0]

    def can_see_goal_post_2(self) -> bool:
        return self.me.can_see_goal_posts()[1]

    def distance_to_goal_opt(self) -> Optional[float]:
        """Distance (in feet) of player that generated this state to the goal."""
        v = self.me.__vector_me_to_goal__()
        if v is None: # I can't calculate vector to puck: probably I can't see the puck.
            return None
        else:
            return v.norm()

    def distance_to_goal(self) -> float:
        """Distance (in feet) of player that generated this state to the goal."""
        return self.me.model.distance_to_goal(self.me.pos)

    def __goal_post_1_closer_than__(self, n_feet: float) -> bool:
        dist_to_goal__post_1_opt, _ = self.me.distance_to_goal_posts()
        return (dist_to_goal__post_1_opt is not None) and (dist_to_goal__post_1_opt <= n_feet)

    def __goal_post_2_closer_than__(self, n_feet: float) -> bool:
        _, dist_to_goal__post_2_opt = self.me.distance_to_goal_posts()
        return (dist_to_goal__post_2_opt is not None) and (dist_to_goal__post_2_opt <= n_feet)

    def __goal_closer_than__(self, n_feet: float) -> bool:
        dist_to_goal_opt = self.distance_to_goal()
        return self.me.can_see_puck() and (dist_to_goal_opt is not None) and (dist_to_goal_opt <= n_feet)

    def goal_post_1_closer_than_10_feet(self) -> bool:
        return self.__goal_post_1_closer_than__(10)

    def goal_post_1_closer_than_20_feet(self) -> bool:
        return self.__goal_post_1_closer_than__(20)

    def goal_post_1_closer_than_30_feet(self) -> bool:
        return self.__goal_post_1_closer_than__(30)

    def goal_post_1_closer_than_40_feet(self) -> bool:
        return self.__goal_post_1_closer_than__(40)

    def goal_post_1_closer_than_50_feet(self) -> bool:
        return self.__goal_post_1_closer_than__(50)

    def goal_post_1_closer_than_60_feet(self) -> bool:
        return self.__goal_post_1_closer_than__(60)

    def goal_post_2_closer_than_10_feet(self) -> bool:
        return self.__goal_post_2_closer_than__(10)

    def goal_post_2_closer_than_20_feet(self) -> bool:
        return self.__goal_post_2_closer_than__(20)

    def goal_post_2_closer_than_30_feet(self) -> bool:
        return self.__goal_post_2_closer_than__(30)

    def goal_post_2_closer_than_40_feet(self) -> bool:
        return self.__goal_post_2_closer_than__(40)

    def goal_post_2_closer_than_50_feet(self) -> bool:
        return self.__goal_post_2_closer_than__(50)

    def goal_post_2_closer_than_60_feet(self) -> bool:
        return self.__goal_post_2_closer_than__(60)

    # angles: this are defined here as the minimum angle between 2 vectors (eg, 20 degrees to the left or to the right)
    def __angle_to_goal_post_1__(self) -> Optional[float]:
        """Irrespective of which side ('right' or 'left')"""
        a1, _ = self.me.angles_to_goal()
        if a1 is None:
            return None
        elif a1.value <= AngleInRadians.PI_HALF:
            return a1.value
        else:
            return AngleInRadians.PI * 2 - a1.value

    def goal_post_1_to_my_right(self) -> bool:
        """Can I See the goal post 1 to my right?"""
        a1, _ = self.me.angles_to_goal()
        return ((a1 is not None) and (a1.value >= AngleInRadians.THREE_HALFS_OF_PI))

    def goal_post_2_to_my_right(self) -> bool:
        """Can I See the goal post 1 to my right?"""
        _, a2 = self.me.angles_to_goal()
        return ((a2 is not None) and (a2.value >= AngleInRadians.THREE_HALFS_OF_PI))


    def __angle_to_goal_post_2__(self) -> Optional[float]:
        """Irrespective of which side ('right' or 'left')"""
        _, a2 = self.me.angles_to_goal()
        if a2 is None:
            return None
        elif a2.value <= AngleInRadians.PI_HALF:
            return a2.value
        else:
            return AngleInRadians.PI * 2 - a2.value

    def __angle_to_goal_post_1_less_than__(self, angle_value: float) -> bool:
        a = self.__angle_to_goal_post_1__()
        return a is not None and a <= angle_value

    def __angle_to_goal_post_2_less_than__(self, angle_value: float) -> bool:
        a = self.__angle_to_goal_post_2__()
        return a is not None and a <= angle_value

    def angle_to_goal_post_1_less_than_pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_2pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=2*AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_3pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=3*AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_4pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=4*AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_5pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=5*AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_6pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=6*AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_7pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=7*AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_8pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=8*AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_9pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=9*AngleInRadians.PI / 10)

    def angle_to_goal_post_1_less_than_10pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_1_less_than__(angle_value=AngleInRadians.PI)


    def angle_to_goal_post_2_less_than_pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_2pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=2*AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_3pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=3*AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_4pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=4*AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_5pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=5*AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_6pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=6*AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_7pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=7*AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_8pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=8*AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_9pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=9*AngleInRadians.PI / 10)

    def angle_to_goal_post_2_less_than_10pi_over_10(self) -> bool:
        return self.__angle_to_goal_post_2_less_than__(angle_value=AngleInRadians.PI)

