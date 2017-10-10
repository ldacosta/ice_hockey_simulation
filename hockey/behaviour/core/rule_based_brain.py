
import random
from typing import List
from hockey.behaviour.core.action import HockeyAction
from hockey.behaviour.core.environment_state import EnvironmentState
# from core.environment_state import EnvironmentState
from core.behaviour import Brain

class RuleBasedBrain(Brain):
    """Rule-based brain."""

    def __init__(self):
        Brain.__init__(self)

    def propose_actions(self, the_state: EnvironmentState) -> List[HockeyAction]:

        if the_state.have_puck():
            # move around - but from time to time, let the puck go
            if random.random() < 0.05:
                return [HockeyAction.SHOOT] # random direction. TODO: how do I express it?
            else:
                return [HockeyAction.MOVE_RANDOM_SPEED]
        else:
            if the_state.my_team_has_puck():
                return [HockeyAction.SPIN_RANDOMLY, HockeyAction.SKATE_CALMLY]
            else:
                if the_state.can_I_reach_puck():
                    return [HockeyAction.GRAB_PUCK]
                else:
                    return [HockeyAction.CHASE_PUCK]
