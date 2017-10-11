import numpy as np
from geometry.vector import Vec2d

from core.behaviour import Brain
from hockey.behaviour.core.action import HockeyAction
from hockey.core.player.base import Player


class Forward(Player):

    def __init__(self, hockey_world_model, brain: Brain):
        super().__init__("forward", hockey_world_model, brain)

    def __parse_action_fwd__(self, a: HockeyAction) -> bool:
        if a == HockeyAction.SHOOT:
            print("FWD -> shoot ==================================================================")
            # TODO: 'towards the goal', unless I don't see it
            self.shoot_puck(direction=Vec2d(tuple(np.random.normal(loc=0.0, scale=5.0, size=2))))
            self.move_around()
        elif a == HockeyAction.PASS:
            print("FWD -> pass ==================================================================")
            pass  # TODO
        else:
            return False
        # wrap-up:
        if self.have_puck:
            self.model.space.place_agent(self.model.puck, self.pos)
        return True

    def act(self) -> bool:
        actions = self.brain.propose_actions(the_state=self.sense())
        if not self.apply_actions(actions, action_handler=self.__parse_action_fwd__):
            return self.apply_actions(actions, action_handler=self.__parse_action__)