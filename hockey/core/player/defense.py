import numpy as np
from typing import List
from random import random
from geometry.point import Point
from geometry.vector import Vec2d

from util.base import normalize_to
from core.behaviour import Brain
from hockey.behaviour.core.action import HockeyAction
from hockey.core.player.base import Player


class Defense(Player):

    def __init__(self, hockey_world_model, brain: Brain):
        super().__init__("defense", hockey_world_model, brain)

    def __parse_action_def__(self, a: HockeyAction) -> bool:
        if a == HockeyAction.SHOOT:
            pt_to_shoot_to = Point(x = 0.0, y = normalize_to(random(), new_min=0, new_max=self.model.height, old_min=0.0, old_max=1.0))
            self.shoot_puck(direction=Vec2d.from_to(from_pt=self.pos, to_pt=pt_to_shoot_to))
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

    def apply_actions(self, actions: List[HockeyAction]) -> bool:
        if not [self.__parse_action_def__(an_action) for an_action in actions][-1]:
            return Player.apply_actions(self, actions)

    def act(self) -> bool:
        actions = self.brain.propose_actions(the_state=self.sense())
        return self.apply_actions(actions)
