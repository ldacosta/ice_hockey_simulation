import numpy as np
from typing import List

from geometry.vector import Vec2d

from core.behaviour import Brain
from hockey.behaviour.core.action import HockeyAction
from hockey.core.player.base import Player


class Forward(Player):

    def __init__(self, hockey_world_model, brain: Brain):
        super().__init__("forward", hockey_world_model, brain)

    def act(self) -> bool:
        actions = self.brain.propose_actions(the_state=self.sense())
        return self.apply_actions(actions)
