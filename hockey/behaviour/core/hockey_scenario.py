
import abc
import random
from typing import Optional
from geometry.point import Point

from xcs.scenarios import Scenario
from xcs.bitstrings import BitString
from util.geometry.lines import StraightLine

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
        # I will remove atomic actions for which I don't want to respond (or don't know how to):
        self.possible_actions.remove(HockeyAction.SHOOT)
        self.possible_actions.remove(HockeyAction.MOVE)
        self.possible_actions.remove(HockeyAction.HARD)
        self.possible_actions.remove(HockeyAction.SOFT)
        self.possible_actions.remove(HockeyAction.LEFT)
        self.possible_actions.remove(HockeyAction.RIGHT)
        self.possible_actions.remove(HockeyAction.RADIANS_0)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_1_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_2_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_3_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_4_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_5_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_6_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_7_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_8_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_9_OVER_10)
        self.possible_actions.remove(HockeyAction.RADIANS_PI_TIMES_10_OVER_10)

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
            # horrible, next 2 lines. Have to put it to reproduce what is done on half-rink. TODO: revisit it!
            self.hockey_world.schedule.steps += 1
            self.hockey_world.schedule.time += 1
            # end-of-TODO
            self.hockey_world.collect_data_if_is_time()
            # self.hockey_world.datacollector.collect(self.hockey_world)
            # beginning of a cycle of sensing.
            goals_before = self.hockey_world.goals_scored
            shots_before = self.hockey_world.shots
            behind_goal_line_before = self.hockey_world.puck.is_behind_goal_line()
            # first thing we do, move the puck! (to be able to track goals/shots and give rewards for it)
            self.hockey_world.puck.step()
            goals_after = self.hockey_world.goals_scored
            shots_after = self.hockey_world.shots
            goal_scored = (goals_after > goals_before)
            self.apply_rewards_for_goal = goal_scored
            self.apply_rewards_for_shot = (shots_after > shots_before)
            # if the puck crossed the end line I will count that as a "try-to-shoot" move:
            self.apply_reward_for_trying_to_shoot = not self.apply_rewards_for_goal and \
                                                    not self.apply_rewards_for_shot and \
                                                    self.hockey_world.puck.is_behind_goal_line() and \
                                                    not behind_goal_line_before
            #
            self.hockey_world.update_running_flag()
            if goal_scored:
                print("[====> half-rink <*******] Goal scored! (now %d in total). Resetting positions of agents" % (self.hockey_world.goals_scored))
                self.hockey_world.reset_positions_of_agents()
        self.player_sensing = self.players_to_sample[self.player_sensing_idx]
        self.player_sensing.update_unable_time()
        bit_string = BitstringEnvironmentState(full_state=self.player_sensing.sense()).as_bitstring()
        return bit_string


class BasicForwardProblem(LearnToPlayHockeyProblem):
    """Rewards for a would-be attacker."""

    reward_get_closer_to_goal = 1  # LearnToPlayHockeyProblem.REWARD_FOR_GOAL/1000
    reward_get_closer_to_puck = reward_get_closer_to_goal
    reward_shot = LearnToPlayHockeyProblem.REWARD_FOR_GOAL / 30  # TODO: we should reward relative to distance from goal...
    reward_get_puck = reward_shot / 10  # reward_get_closer_to_puck * 100
    bonus_for_having_puck = 10 * max(reward_get_closer_to_goal, reward_get_closer_to_puck) + 1
    punishment_action_failed = -reward_get_closer_to_goal/2

    def __init__(self, hockey_world: HockeyHalfRink):
        LearnToPlayHockeyProblem.__init__(self, hockey_world)
        print("reward_get_closer_to_goal = %.2f" % (self.reward_get_closer_to_goal))
        print("reward_get_closer_to_puck = %.2f" % (self.reward_get_closer_to_puck))
        print("reward_shot = %.2f" % (self.reward_shot))
        print("bonus_for_having_puck = %.2f" % (self.bonus_for_having_puck))

    def execute(self, action) -> Optional[float]:
        # first, let's get the player to execute this action on his/her environment:
        if self.player_sensing is None:
            return None
        else:
            # scheme of rewards
            #
            distance_to_goal_before = self.hockey_world.distance_to_goal(self.player_sensing.pos)
            distance_to_puck_before = self.hockey_world.distance_to_puck(self.player_sensing.pos)
            have_puck_before = self.player_sensing.have_puck
            action_successful = self.player_sensing.apply_actions([action]) # TODO: should I penalize for impossible actions (eg, shooting when puck is not owned. Function returns 'False' in that case).
            distance_to_goal_after = self.hockey_world.distance_to_goal(self.player_sensing.pos)
            distance_to_puck_after = self.hockey_world.distance_to_puck(self.player_sensing.pos)
            have_puck_after = self.player_sensing.have_puck
            # sanity checking
            if action == HockeyAction.GRAB_PUCK:
                assert (action_successful == have_puck_after)

            reward = 0  # TODO: seriously???? I thought it would be None !
            if self.apply_rewards_for_goal:
                print("APPLY REWARD FOR GOAL")
                reward = LearnToPlayHockeyProblem.REWARD_FOR_GOAL
            elif self.apply_rewards_for_shot:
                print("APPLY REWARD FOR SHOT")
                reward = self.reward_shot
            elif self.apply_reward_for_trying_to_shoot:
                sl = StraightLine.goes_by(
                    point_1=(0, self.reward_shot),
                    point_2=((self.hockey_world.WIDTH_HALF_ICE - self.hockey_world.GOALIE_WIDTH) / 2,
                             0))  # TODO: factorize this, take it out of here.
                dist = self.hockey_world.distance_to_closest_goal_post(self.hockey_world.puck.pos)
                reward = sl.apply_to(an_x=dist)
                print(
                    "Apply reward for trying to shoot: distance is %.2f feet, reward is %.2f (for an actual shot is %.2f)" % (
                    dist, reward, self.reward_shot))
            elif not action_successful: # if action was unsuccessful, let's clear the deck:
                reward = self.punishment_action_failed
            if action_successful:
                if have_puck_after:
                    # print("HAVE PUCK")
                    # I still have the puck. Did I get closer to goal?
                    reward += self.bonus_for_having_puck
                    if distance_to_goal_before > distance_to_goal_after:
                        # print("HAVE PUCK, GOT CLOSER TO GOAL => reward = %.2f" % (reward_get_closer_to_goal))
                        # print("=====> and I'm closer to goal!")
                        reward += self.reward_get_closer_to_goal
                    elif distance_to_goal_before < distance_to_goal_after:
                        reward -= self.reward_get_closer_to_goal
                else:
                    # print("DON'T HAVE PUCK")
                    # didn't have puck before, I don't have it now. Did I get closer to puck?
                    if distance_to_puck_before > distance_to_puck_after:
                        # print("[HAVE NO PUCK] GOT CLOSER TO PUCK")
                        reward += self.reward_get_closer_to_puck
                    elif distance_to_puck_before < distance_to_puck_after:
                        # print("[HAVE NO PUCK] GOT FARTHER FROM PUCK => reward = %.2f" % (-reward_get_closer_to_puck))
                        reward += -self.reward_get_closer_to_puck
            # if reward > 0:
            #     print("returning reward %.2f" % (reward))
            return reward

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
