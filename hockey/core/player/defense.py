import numpy as np
from geometry.vector import Vec2d

from core.behaviour import Brain
from hockey.behaviour.core.action import HockeyAction
from hockey.core.player.base import Player


class Defense(Player):

    def __init__(self, hockey_world_model, brain: Brain):
        super().__init__("defense", hockey_world_model, brain)

    def __parse_action_def__(self, a: HockeyAction) -> bool:
        if a == HockeyAction.SHOOT:
            # TODO: 'away from goal'
            self.shoot_puck(direction=Vec2d(tuple(np.random.normal(loc=0.0, scale=5.0, size=2))))
            self.move_around()
        elif a == HockeyAction.PASS:
            print("DEFENSE -> pass TODO =============================================================")
            pass  # TODO
        else:
            return False
        # wrap-up:
        if self.have_puck:
            self.model.space.place_agent(self.model.puck, self.pos)
        return True

    def act(self) -> bool:
        actions = self.brain.propose_actions(the_state=self.sense())
        if not self.apply_actions(actions, action_handler=self.__parse_action_def__):
            return self.apply_actions(actions, action_handler=self.__parse_action__)