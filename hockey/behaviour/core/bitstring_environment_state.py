
from typing import List, Optional
from xcs.bitstrings import BitString as XCSBitString, BitCondition
from geometry.angle import AngleInRadians
from hockey.behaviour.core.environment_state import EnvironmentState


def angle_to_bitstring(can_see: bool, angle_opt: Optional[AngleInRadians], num_slices_on_angles: int) -> XCSBitString:
    assert num_slices_on_angles > 0
    as_list = []
    # can I see the puck?
    can_see_as_int = int(can_see)
    # angles:
    # (1) to puck (if I can see puck only! Otherwise I can't evaluate the angle!)
    match_on_last = False
    for slice in range(0, num_slices_on_angles + 1):
        angle_for_slice = slice * AngleInRadians.PI / num_slices_on_angles
        match_on_this = (angle_opt is not None) and (angle_opt.value <= angle_for_slice)
        as_list.append(int(match_on_this and not match_on_last) * can_see_as_int)
        match_on_last = match_on_last or match_on_this
    return XCSBitString(as_list)

def distance_to_bitstring(can_see: bool, distance_opt: Optional[float], range_distances: List[float]) -> XCSBitString:
    assert len(range_distances) > 0
    if distance_opt is None:
        distance = float("inf")
    else:
        distance = distance_opt
    as_list = []
    # can I see the puck?
    can_see_as_int = int(can_see)
    # (1) to puck (if I can see puck only! Otherwise I can't evaluate the distance!)
    match_on_last = False
    for distance_to_evaluate in range_distances:
        match_on_this = distance <= distance_to_evaluate
        as_list.append(int(match_on_this and not match_on_last) * can_see_as_int)
        match_on_last = match_on_last or match_on_this
    return XCSBitString(as_list)

def is_closer_than(can_see: bool, distance: float, cmp_distance: float) -> bool:
    return can_see and (distance <= cmp_distance)

# class BitDescription(object):
#
#     def __init__

class BitstringEnvironmentState(object):

    # all the functions must exist in self.full_state
    bit_fns = ['attacking',
               'have_puck',
               'my_team_has_puck',
               'can_I_reach_puck',
               # ***** distances
               # puck
               'can_see_puck',
               'puck_closer_than_10_feet',
               'puck_closer_than_20_feet',
               'puck_closer_than_30_feet',
               'puck_closer_than_40_feet',
               'puck_closer_than_50_feet',
               'puck_closer_than_60_feet',
               # goal
               'can_see_goal_post_1',
               'goal_post_1_closer_than_10_feet',
               'goal_post_1_closer_than_20_feet',
               'goal_post_1_closer_than_30_feet',
               'goal_post_1_closer_than_40_feet',
               'goal_post_1_closer_than_50_feet',
               'goal_post_1_closer_than_60_feet',
               'can_see_goal_post_2',
               'goal_post_2_closer_than_10_feet',
               'goal_post_2_closer_than_20_feet',
               'goal_post_2_closer_than_30_feet',
               'goal_post_2_closer_than_40_feet',
               'goal_post_2_closer_than_50_feet',
               'goal_post_2_closer_than_60_feet',
               # ***** angles
               # puck
               'puck_to_my_right',
               'angle_to_puck_less_than_pi_over_10',
               'angle_to_puck_less_than_2pi_over_10',
               'angle_to_puck_less_than_3pi_over_10',
               'angle_to_puck_less_than_4pi_over_10',
               'angle_to_puck_less_than_5pi_over_10',
               'angle_to_puck_less_than_6pi_over_10',
               'angle_to_puck_less_than_7pi_over_10',
               'angle_to_puck_less_than_8pi_over_10',
               'angle_to_puck_less_than_9pi_over_10',
               'angle_to_puck_less_than_10pi_over_10',
               # goal post 1
               'goal_post_1_to_my_right',
               'angle_to_goal_post_1_less_than_pi_over_10',
               'angle_to_goal_post_1_less_than_2pi_over_10',
               'angle_to_goal_post_1_less_than_3pi_over_10',
               'angle_to_goal_post_1_less_than_4pi_over_10',
               'angle_to_goal_post_1_less_than_5pi_over_10',
               'angle_to_goal_post_1_less_than_6pi_over_10',
               'angle_to_goal_post_1_less_than_7pi_over_10',
               'angle_to_goal_post_1_less_than_8pi_over_10',
               'angle_to_goal_post_1_less_than_9pi_over_10',
               'angle_to_goal_post_1_less_than_10pi_over_10',
               # goal post 1
               'goal_post_2_to_my_right',
               'angle_to_goal_post_2_less_than_pi_over_10',
               'angle_to_goal_post_2_less_than_2pi_over_10',
               'angle_to_goal_post_2_less_than_3pi_over_10',
               'angle_to_goal_post_2_less_than_4pi_over_10',
               'angle_to_goal_post_2_less_than_5pi_over_10',
               'angle_to_goal_post_2_less_than_6pi_over_10',
               'angle_to_goal_post_2_less_than_7pi_over_10',
               'angle_to_goal_post_2_less_than_8pi_over_10',
               'angle_to_goal_post_2_less_than_9pi_over_10',
               'angle_to_goal_post_2_less_than_10pi_over_10',
               ]

    @classmethod
    def explain_condition(cls, condition: BitCondition):
        assert len(condition) == len(cls.bit_fns)
        v = [("%s = %s" % (cls.bit_fns[i], bool(v))) for i, v in enumerate(condition) if v is not None]
        return '; \n'.join(v)

    def build_defs(self):
        return list(map(lambda function_name: int(getattr(self.full_state, function_name)()),
                        BitstringEnvironmentState.bit_fns))

    NUM_SLICES_ON_ANGLES = 20 # how many slices I want to see in [0, Pi]
    DISTANCE_RANGE = list(range(10, 60 + 1, 10)) # distances I want to bitcheck for

    def __init__(self, full_state: EnvironmentState):
        self.full_state = full_state
        self.r_bitstring = XCSBitString(self.build_defs())

    def as_bitstring(self) -> XCSBitString:
        """Builds a bitstring out of the information sensed by an agent."""

        # ok then! Return!
        return self.r_bitstring
