
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

        return XCSBitString(as_list)


