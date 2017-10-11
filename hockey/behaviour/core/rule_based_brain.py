
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
        actions = []
        if the_state.have_puck():
            # move around - but from time to time, let the puck go
            if random.random() < 0.05:
                actions.append(HockeyAction.SHOOT)
            else:
                actions.append(HockeyAction.MOVE_RANDOM_SPEED)
        else:
            if the_state.my_team_has_puck():
                if random.random() < 0.05:
                    actions.append(HockeyAction.SPIN_RANDOMLY)
                actions.append(HockeyAction.SKATE_CALMLY)
            else:
                if the_state.can_I_reach_puck():
                    actions.append(HockeyAction.GRAB_PUCK)
                else:
                    actions.append(HockeyAction.CHASE_PUCK)
        return actions
