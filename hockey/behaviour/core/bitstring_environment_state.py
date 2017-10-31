
from xcs.bitstrings import BitString as XCSBitString
from hockey.behaviour.core.environment_state import EnvironmentState

class BitstringEnvironmentState(object):

    def __init__(self, full_state: EnvironmentState):
        self.full_state = full_state

    def as_bitstring(self) -> XCSBitString:
        as_list = []
        as_list.append(int(self.full_state.have_puck()))
        as_list.append(int(self.full_state.my_team_has_puck()))
        as_list.append(int(self.full_state.can_I_reach_puck()))
        # can I see the puck?
        can_see_puck_as_int = int(self.full_state.me.can_see_puck())
        as_list.append(can_see_puck_as_int)
        # distances:
        # (1) to puck (if I can see puck only! Otherwise I can't evaluate the distance!)
        dist_to_puck = self.full_state.distance_to_puck()
        as_list.append(int(dist_to_puck <= 10) * can_see_puck_as_int)
        as_list.append(int((dist_to_puck > 10) and (dist_to_puck <= 20)) * can_see_puck_as_int)
        as_list.append(int((dist_to_puck > 20) and (dist_to_puck <= 30)) * can_see_puck_as_int)
        as_list.append(int((dist_to_puck > 30) and (dist_to_puck <= 40)) * can_see_puck_as_int)
        as_list.append(int((dist_to_puck > 40) and (dist_to_puck <= 50)) * can_see_puck_as_int)
        as_list.append(int((dist_to_puck > 50) and (dist_to_puck <= 60)) * can_see_puck_as_int)
        as_list.append(int(dist_to_puck > 60) * can_see_puck_as_int)
        # (2) to goal
        # can I see the goal?
        can_see_goal_as_int = int(self.full_state.me.can_see_goal())
        as_list.append(can_see_goal_as_int)
        dist_to_goal = self.full_state.distance_to_goal()
        as_list.append(int(dist_to_goal <= 10) * can_see_puck_as_int)
        as_list.append(int((dist_to_goal > 10) and (dist_to_goal <= 20)) * can_see_goal_as_int)
        as_list.append(int((dist_to_goal > 20) and (dist_to_goal <= 30)) * can_see_goal_as_int)
        as_list.append(int((dist_to_goal > 30) and (dist_to_goal <= 40)) * can_see_goal_as_int)
        as_list.append(int((dist_to_goal > 40) and (dist_to_goal <= 50)) * can_see_goal_as_int)
        as_list.append(int((dist_to_goal > 50) and (dist_to_goal <= 60)) * can_see_goal_as_int)
        as_list.append(int(dist_to_goal > 60) * can_see_goal_as_int)
        # ok then! Return!
        return XCSBitString(as_list)


