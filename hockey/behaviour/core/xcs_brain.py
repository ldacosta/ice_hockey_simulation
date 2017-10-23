
import random
from typing import Optional

from xcs.scenarios import Scenario
from xcs.bitstrings import BitString

from hockey.core.half_rink import HockeyHalfRink
from hockey.behaviour.core.action import HockeyAction
from hockey.behaviour.core.bitstring_environment_state import BitstringEnvironmentState

class LearnToPlayHockeyProblem(Scenario):
    """Learning to play soccer with XCS"""

    def __init__(self, hockey_world: HockeyHalfRink):
        self.possible_actions = list(HockeyAction)
        self.hockey_world = hockey_world
        self.reset()

    @property
    def is_dynamic(self):
        return True

    def get_possible_actions(self):
        return self.possible_actions

    def reset_players(self):
        self.players_to_sample = self.hockey_world.defense + self.hockey_world.attack
        random.shuffle(self.players_to_sample)
        self.player_sensing = None


    def reset(self):
        self.goals_before = 0
        self.reset_players()

    def more(self) -> bool:
        return self.hockey_world.running

    def sense(self) -> BitString:
        # senses each one of the players in the world, one after the other
        if len(self.players_to_sample) == 0:
            # sampled everyone. Move the puck, make world tick, restart.
            self.hockey_world.puck.step()
            self.hockey_world.datacollector.collect(self.hockey_world)
            # horrible, next 2 lines. Have to put it to reproduce what is done on half-rink. TODO: revisit it!
            self.hockey_world.schedule.steps += 1
            self.hockey_world.schedule.time += 1
            # end-of-TODO
            self.hockey_world.update_running_flag()
            if self.hockey_world.goals_scored > self.goals_before:
                print("[half-rink] Goal scored! (now %d in total). Resetting positions of agents" % (self.hockey_world.goals_scored))
                self.hockey_world.reset_positions_of_agents()
            #
            self.reset_players()
            self.goals_before = self.hockey_world.goals_scored
        self.player_sensing = self.players_to_sample[0]
        self.players_to_sample = self.players_to_sample[1:]
        return BitstringEnvironmentState(full_state=self.player_sensing.sense()).as_bitstring()

    def execute(self, action) -> Optional[float]:
        # first, let's get the player to execute this action on his/her environment:
        if self.player_sensing is None:
            return None
        else:
            goals_before = self.hockey_world.goals_scored
            self.player_sensing.apply_actions([action])
            if self.hockey_world.goals_scored > goals_before:
                return 1.0 # reward!!!!
            else:
                return 0.0 # TODO: seriously???? I thought it would be None !
