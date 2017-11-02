
from typing import List
from xcs.bitstrings import BitString as XCSBitString
from geometry.angle import AngleInRadians
from hockey.behaviour.core.environment_state import EnvironmentState


def angle_to_bitstring(can_see: bool, angle: AngleInRadians, num_slices_on_angles: int) -> XCSBitString:
    assert num_slices_on_angles > 0
    as_list = []
    # can I see the puck?
    can_see_as_int = int(can_see)
    # angles:
    # (1) to puck (if I can see puck only! Otherwise I can't evaluate the angle!)
    match_on_last = False
    for slice in range(0, num_slices_on_angles + 1):
        angle_for_slice = slice * AngleInRadians.PI / num_slices_on_angles
        match_on_this = angle.value <= angle_for_slice
        as_list.append(int(match_on_this and not match_on_last) * can_see_as_int)
        match_on_last = match_on_last or match_on_this
    return XCSBitString(as_list)

def distance_to_bitstring(can_see: bool, distance: float, range_distances: List[float]) -> XCSBitString:
    assert len(range_distances) > 0
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

class BitstringEnvironmentState(object):

    NUM_SLICES_ON_ANGLES = 20 # how many slices I want to see in [0, Pi]
    DISTANCE_RANGE = list(range(10, 60 + 1, 10)) # distances I want to bitcheck for

    def __init__(self, full_state: EnvironmentState):
        self.full_state = full_state

    def as_bitstring(self) -> XCSBitString:
        """Builds a bitstring out of the information sensed by an agent."""

        r_bitstring = XCSBitString([int(self.full_state.attacking)])
        r_bitstring += XCSBitString([int(self.full_state.have_puck())])
        r_bitstring += XCSBitString([int(self.full_state.my_team_has_puck())])
        r_bitstring += XCSBitString([int(self.full_state.can_I_reach_puck())])
        # Puck related stuff
        # can I see the puck?
        can_see_puck_as_int = int(self.full_state.me.can_see_puck())
        r_bitstring += XCSBitString([can_see_puck_as_int])
        # distances:
        dist_to_puck = self.full_state.distance_to_puck()
        r_bitstring += distance_to_bitstring(can_see=self.full_state.me.can_see_puck(),
                                                     distance=dist_to_puck,
                                                     range_distances=self.DISTANCE_RANGE)
        # angles
        r_bitstring += angle_to_bitstring(can_see=self.full_state.me.can_see_puck(),
                                          angle=self.full_state.me.angle_to_puck(),
                                          num_slices_on_angles=self.NUM_SLICES_ON_ANGLES)
        # Goal related stuff
        # can I see the goal?
        can_see_goal_as_int = int(self.full_state.me.can_see_goal())
        r_bitstring += XCSBitString([can_see_goal_as_int])
        # distances:
        dist_to_goal = self.full_state.distance_to_goal()
        r_bitstring += distance_to_bitstring(can_see=self.full_state.me.can_see_goal(),
                                                     distance=dist_to_goal,
                                                     range_distances=self.DISTANCE_RANGE)
        # angles:
        r_bitstring += angle_to_bitstring(can_see=self.full_state.me.can_see_puck(),
                                          angle=self.full_state.me.min_angle_to_goal(),
                                          num_slices_on_angles=self.NUM_SLICES_ON_ANGLES)
        # ok then! Return!
        return r_bitstring
