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
            pt_in_goal_opt = self.first_visible_goal_point()
            if pt_in_goal_opt is None:
                direction = Vec2d(tuple(np.random.normal(loc=0.0, scale=5.0, size=2)))
                scoring_prob = 0.0
            else:
                direction = Vec2d.from_to(from_pt=self.pos, to_pt=pt_in_goal_opt)
                scoring_prob = self.model.prob_of_scoring_from(self.pos)
                print("[%s] shot TOWARDS THE GOAL (from %s to %s, distance = %.2f feet), prob of scoring = %.2f" % (self.unique_id, self.pos, pt_in_goal_opt, self.model.distance_to_goal(self.pos), scoring_prob))
            self.shoot_puck(direction)
            self.model.puck.prob_of_goal = scoring_prob
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