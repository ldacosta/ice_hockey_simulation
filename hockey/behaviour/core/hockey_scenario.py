
import abc
import random
from typing import Optional

from xcs.scenarios import Scenario
from xcs.bitstrings import BitString

from hockey.core.half_rink import HockeyHalfRink
from hockey.behaviour.core.action import HockeyAction
from hockey.behaviour.core.bitstring_environment_state import BitstringEnvironmentState

from hockey.core.player.base import Player

class PlayerMetrics(object):

    def __init__(self, a_player: Player):
        self.player = a_player
        self.update()

    def update(self):
        self.goals = self.player.model.goals_scored
        self.shots = self.player.model.shots
        self.distance_to_goal = self.player.model.distance_to_goal(self.player.pos)
        self.distance_to_puck = self.player.model.distance_to_puck(self.player.pos)
        self.have_puck = self.player.have_puck


class LearnToPlayHockeyProblem(Scenario, metaclass=abc.ABCMeta):
    """Learning to play soccer with XCS"""

    REWARD_FOR_GOAL = 1000.0

    def __init__(self, hockey_world: HockeyHalfRink):
        self.possible_actions = list(HockeyAction)
        self.hockey_world = hockey_world
        self.players_to_sample = self.hockey_world.defense + self.hockey_world.attack
        random.shuffle(self.players_to_sample)
        self.players_metrics = list(map(PlayerMetrics, self.players_to_sample))
        self.player_sensing_idx = 0
        self.reset()

    @property
    def is_dynamic(self):
        return True

    def get_possible_actions(self):
        return self.possible_actions

    def reset_players(self):
        self.player_sensing_idx = 0
        self.player_sensing = None

    def reset(self):
       self.reset_players()

    def more(self) -> bool:
        return self.hockey_world.running

    def sense(self) -> BitString:
        # senses each one of the players in the world, one after the other
        self.player_sensing_idx = (self.player_sensing_idx + 1) % len(self.players_to_sample)
        if self.player_sensing_idx == 0:
            # sampled everyone. Move the puck, make world tick, restart.
            self.hockey_world.datacollector.collect(self.hockey_world)
            # horrible, next 2 lines. Have to put it to reproduce what is done on half-rink. TODO: revisit it!
            self.hockey_world.schedule.steps += 1
            self.hockey_world.schedule.time += 1
            # end-of-TODO
            # beginning of a cycle of sensing.
            goals_before = self.hockey_world.goals_scored
            shots_before = self.hockey_world.shots
            # first thing we do, move the puck! (to be able to track goals/shots and give rewards for it)
            self.hockey_world.puck.step()
            goals_after = self.hockey_world.goals_scored
            shots_after = self.hockey_world.shots
            goal_scored = (goals_after > goals_before)
            self.apply_rewards_for_goal = goal_scored
            self.apply_rewards_for_shot = (shots_after > shots_before)
            #
            self.hockey_world.update_running_flag()
            if goal_scored:
                print("[====> half-rink <*******] Goal scored! (now %d in total). Resetting positions of agents" % (self.hockey_world.goals_scored))
                self.hockey_world.reset_positions_of_agents()
        self.player_sensing = self.players_to_sample[self.player_sensing_idx]
        return BitstringEnvironmentState(full_state=self.player_sensing.sense()).as_bitstring()


class BasicForwardProblem(LearnToPlayHockeyProblem):
    """Rewards for a would-be attacker."""

    def execute(self, action) -> Optional[float]:
        # first, let's get the player to execute this action on his/her environment:
        if self.player_sensing is None:
            return None
        else:
            # scheme of rewards
            reward_get_closer_to_goal = LearnToPlayHockeyProblem.REWARD_FOR_GOAL/1000
            reward_get_closer_to_puck = reward_get_closer_to_goal
            reward_shot = LearnToPlayHockeyProblem.REWARD_FOR_GOAL/30 # TODO: we should reward relative to distance from goal...
            reward_get_puck = reward_shot / 10 # reward_get_closer_to_puck * 100
            #
            distance_to_goal_before = self.hockey_world.distance_to_goal(self.player_sensing.pos)
            distance_to_puck_before = self.hockey_world.distance_to_puck(self.player_sensing.pos)
            have_puck_before = self.player_sensing.have_puck
            self.player_sensing.apply_actions([action]) # TODO: should I pensalize for impossible actions (eg, shooting when puck is not owned. Function returns 'False' in that case).
            distance_to_goal_after = self.hockey_world.distance_to_goal(self.player_sensing.pos)
            distance_to_puck_after = self.hockey_world.distance_to_puck(self.player_sensing.pos)
            have_puck_after = self.player_sensing.have_puck
            # let's do it!
            if self.apply_rewards_for_goal:
                print("APPLY REWARD FOR GOAL => reward = %.2f" % (LearnToPlayHockeyProblem.REWARD_FOR_GOAL))
                return LearnToPlayHockeyProblem.REWARD_FOR_GOAL
            elif self.apply_rewards_for_shot:
                print("APPLY REWARD FOR SHOT => reward = %.2f" % (reward_shot))
                return reward_shot
            elif have_puck_before:
                if not have_puck_after:
                    print("LOST PUCK => reward = %.2f" % (-reward_get_puck))
                    # return -reward_get_puck
                else:
                    # I still have the puck. Did I get closer to goal?
                    if distance_to_goal_before > distance_to_goal_after:
                        print("HAVE PUCK, GOT CLOSER TO GOAL => reward = %.2f" % (reward_get_closer_to_goal))
                        return reward_get_closer_to_goal
                    # elif distance_to_goal_before < distance_to_goal_after:
                    #     print("HAVE PUCK, GOT FARTHER FROM GOAL => reward = %.2f" % (-reward_get_closer_to_goal))
                    #     return -reward_get_closer_to_goal
            else: # I did not have the puck before!
                if have_puck_after:
                    print("GOT PUCK => reward = %.2f" % (reward_get_puck))
                    return reward_get_puck
                else:
                    # didn't have puck before, I don't have it now. Did I get closer to puck?
                    if distance_to_puck_before > distance_to_puck_after:
                        # print("[HAVE NO PUCK] GOT CLOSER TO PUCK => reward = %.2f" % (reward_get_closer_to_puck))
                        return reward_get_closer_to_puck
                    # elif distance_to_puck_before < distance_to_puck_after:
                    #     # print("[HAVE NO PUCK] GOT FARTHER FROM PUCK => reward = %.2f" % (-reward_get_closer_to_puck))
                    #     return -reward_get_closer_to_puck
            return 0 # TODO: seriously???? I thought it would be None !

class Full5On5Rewards(LearnToPlayHockeyProblem):
    """Rewards for 5x5 hockey."""

    def execute(self, action) -> Optional[float]:
        if self.player_sensing is None:
            return None
        else:
            goals_before = self.hockey_world.goals_scored
            #  let's get the player to execute this action on his/her environment:
            self.player_sensing.apply_actions([action])
            if self.hockey_world.goals_scored > goals_before:
                return 1.0 # reward!!!!
            else:
                return 0 # TODO: seriously???? I thought it would be None !
