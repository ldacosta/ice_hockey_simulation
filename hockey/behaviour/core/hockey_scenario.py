#!/usr/bin/env python
"""A piece of ice.

"""

import abc
import random
import time

from typing import Optional
from xcs.bitstrings import BitString
from xcs.scenarios import Scenario

from hockey.behaviour.core.action import HockeyAction
from hockey.behaviour.core.bitstring_environment_state import BitstringEnvironmentState
from hockey.core.ice_surface.ice_rink import SkatingIce


class LearnToPlayHockeyProblem(Scenario, metaclass=abc.ABCMeta):
    """Learning to play soccer with XCS"""

    REWARD_FOR_GOAL = 1000.0

    def __init__(self, piece_of_ice: SkatingIce):
        self.possible_actions = list(HockeyAction)
        # I will remove atomic actions for which I don't want to respond (or don't know how to):
        self.possible_actions.remove(HockeyAction.SHOOT)
        self.possible_actions.remove(HockeyAction.MOVE)
        self.possible_actions.remove(HockeyAction.FULL_POWER)
        self.possible_actions.remove(HockeyAction.HALF_POWER)
        self.possible_actions.remove(HockeyAction.THIRD_OF_POWER)
        self.possible_actions.remove(HockeyAction.MIN_POWER)
        self.possible_actions.remove(HockeyAction.NO_POWER)
        self.possible_actions.remove(HockeyAction.KEEP_SPEED)
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

        for action in self.possible_actions:
            print(action)

        self.hockey_world = piece_of_ice
        self.players_to_sample = self.hockey_world.defense + self.hockey_world.attack
        random.shuffle(self.players_to_sample)
        self.player_sensing_idx = 0
        self.episode_finished = False
        self.reset_players_and_puck()
        self.hockey_world.reset()

    @property
    def is_dynamic(self):
        return True

    def get_possible_actions(self):
        return self.possible_actions

    def reset_players_and_puck(self):
        self.player_sensing_idx = 0
        self.player_sensing = None
        self.puck_turn_idx = random.randint(0, len(self.players_to_sample)) + 1

    def reset(self):
        self.episode_finished = False
        self.reset_players_and_puck()
        self.hockey_world.reset()
        self.episode_start_in_secs = self.seconds_in_simulation()
        print("[scenario reset] ice world = %s" % (self.hockey_world))
        # sanity check
        assert not self.hockey_world.puck.is_taken

    def seconds_in_simulation(self) -> int:
        return self.hockey_world.schedule.steps * self.hockey_world.one_step_in_seconds

    def more(self) -> bool:
        if self.episode_finished:
            print("%d seconds (minute %d) elapsed in simulation **************** Episode finished (lasted %.2f secs), resetting stuff **************" %
                  (self.seconds_in_simulation(), self.seconds_in_simulation() // 60, self.seconds_in_simulation() - self.episode_start_in_secs))
            self.update_world_simulation()
        return (not self.episode_finished) and self.hockey_world.running

    def update_world_simulation(self):
        # horrible, next 2 lines. Have to put it to reproduce what is done on half-rink. TODO: revisit it!
        self.hockey_world.schedule.steps += 1
        self.hockey_world.schedule.time += 1
        # end-of-TODO
        self.hockey_world.collect_data_if_is_time()
        # self.hockey_world.datacollector.collect(self.hockey_world)
        self.hockey_world.update_running_flag()

    def sense(self) -> BitString:
        # senses each one of the players in the world, one after the other
        self.player_sensing_idx = (self.player_sensing_idx + 1) % len(self.players_to_sample)
        if self.player_sensing_idx == 0:
            # sampled everyone. Move the puck, make world tick, restart.
            self.update_world_simulation()
            self.puck_turn_idx = random.randint(0, len(self.players_to_sample))
        self.player_sensing = self.players_to_sample[self.player_sensing_idx]
        self.player_sensing.update_unable_time()
        return BitstringEnvironmentState(full_state=self.player_sensing.sense()).as_bitstring()

class Feedback(object):

    def __init__(self, simulation_seconds: int, real_date_str: str):
        self.reset_to(simulation_seconds, real_date_str)

    def reset_to(self, simulation_seconds: int, real_date_str: str):
        self.seconds_in_simulation = simulation_seconds
        self.timestamp_simulation_str = "Minute %d:%02d" % (self.seconds_in_simulation // 60, int(round(self.seconds_in_simulation % 60)))
        self.real_date_str = real_date_str
        self.msgs = []

    def is_empty(self):
        return len(self.msgs) == 0

    def __iadd__(self, a_msg: str):
        self.msgs.append(a_msg)
        return self

    def __str__(self):
        a_str = "[%s] Simulation time: %s" % (self.real_date_str, self.timestamp_simulation_str)
        for msg in self.msgs:
            a_str += "\n\t " + msg
        return a_str


class GrabThePuckProblem(LearnToPlayHockeyProblem):
    """Rewards for a would-be attacker."""

    reward_shot = LearnToPlayHockeyProblem.REWARD_FOR_GOAL / 30  # TODO: we should reward relative to distance from goal...
    reward_get_puck = reward_shot / 10  # reward_get_closer_to_puck * 100
    punishment_action_failed = -1/2
    punishment_loss_energy = -1 # each time step, I lose energy

    def __init__(self, hockey_world: SkatingIce):
        LearnToPlayHockeyProblem.__init__(self, hockey_world)
        print("reward_shot = %.2f" % (GrabThePuckProblem.reward_shot))
        print("reward_get_puck = %.2f" % (GrabThePuckProblem.reward_get_puck))
        print("punishment_action_failed = %.2f" % (GrabThePuckProblem.punishment_action_failed))
        print("punishment_loss_energy = %.2f" % (GrabThePuckProblem.punishment_loss_energy))
        self.seconds_in_simulation_last_feedback = -1 # when was the last time I gave feedback?
        self.feedback = Feedback(simulation_seconds=0, real_date_str=time.ctime())

    def execute(self, action) -> Optional[float]:
        def add_to_feedback(msg: str, force: bool = False):
            """Potentially adds to feedback."""
            if (not self.feedback.is_empty()) or (force):
                self.feedback += msg

        # first, let's get the player to execute this action on his/her environment:
        if self.player_sensing is None:
            return None
        else:
            action_successful = self.player_sensing.apply_actions([action]) # TODO: should I penalize for impossible actions (eg, shooting when puck is not owned. Function returns 'False' in that case).
            have_puck_after = self.player_sensing.have_puck

            seconds_in_simulation = self.seconds_in_simulation()
            self.feedback.reset_to(simulation_seconds=seconds_in_simulation, real_date_str=time.ctime())
            if (self.seconds_in_simulation_last_feedback < 0) or \
                    (self.seconds_in_simulation_last_feedback <= seconds_in_simulation - 3 * 60):
                add_to_feedback("%d seconds (minute %d) elapsed in simulation" % (seconds_in_simulation, seconds_in_simulation // 60), force=True)
                self.seconds_in_simulation_last_feedback = seconds_in_simulation
            reward = GrabThePuckProblem.punishment_loss_energy # agent loses energy by default
            # Rewards related to the action I did last:
            if not action_successful: # if action was unsuccessful, let's clear the deck:
                reward += self.punishment_action_failed
                add_to_feedback("Action '%s' not successful. Cumulated reward = %.2f" % (action, reward))
            else:
                if have_puck_after:
                    reward += self.reward_get_puck
                    add_to_feedback("Grabbed puck! (cumulated reward is %.2f)" % (reward), force=True)

            if self.puck_turn_idx == self.player_sensing_idx + 1:
                self.hockey_world.puck.step() # ok then, move the puck!
            # has this episode finished?
            self.episode_finished = have_puck_after
            if have_puck_after:
                add_to_feedback("Agent [%s] has the puck, episode finished." % (self.player_sensing.unique_id))
            if not self.feedback.is_empty():
                add_to_feedback("[action: %s]  ===============> returning reward %.2f" % (action, reward))
                print("%s" % (self.feedback))
                self.seconds_in_simulation_last_feedback = seconds_in_simulation
            return reward

class ScoreAGoalProblem(LearnToPlayHockeyProblem):
    """Rewards for a would-be attacker."""

    reward_shot = LearnToPlayHockeyProblem.REWARD_FOR_GOAL / 30  # TODO: we should reward relative to distance from goal...
    reward_get_puck = reward_shot / 10  # reward_get_closer_to_puck * 100
    punishment_action_failed = -1/2
    punishment_loss_energy = -1 # each time step, I lose energy

    def __init__(self, hockey_world: SkatingIce):
        LearnToPlayHockeyProblem.__init__(self, hockey_world)
        print("reward_shot = %.2f" % (GrabThePuckProblem.reward_shot))
        print("reward_get_puck = %.2f" % (GrabThePuckProblem.reward_get_puck))
        print("punishment_action_failed = %.2f" % (GrabThePuckProblem.punishment_action_failed))
        print("punishment_loss_energy = %.2f" % (GrabThePuckProblem.punishment_loss_energy))
        self.seconds_in_simulation_last_feedback = -1 # when was the last time I gave feedback?
        self.feedback = Feedback(simulation_seconds=0, real_date_str=time.ctime())

    def execute(self, action) -> Optional[float]:
        def add_to_feedback(msg: str, force: bool = False):
            """Potentially adds to feedback."""
            if (not self.feedback.is_empty()) or (force):
                self.feedback += msg

        # first, let's get the player to execute this action on his/her environment:
        if self.player_sensing is None:
            return None
        else:
            action_successful = self.player_sensing.apply_actions([action]) # TODO: should I penalize for impossible actions (eg, shooting when puck is not owned. Function returns 'False' in that case).
            have_puck_after = self.player_sensing.have_puck

            seconds_in_simulation = self.seconds_in_simulation()
            self.feedback.reset_to(simulation_seconds=seconds_in_simulation, real_date_str=time.ctime())
            if (self.seconds_in_simulation_last_feedback < 0) or \
                    (self.seconds_in_simulation_last_feedback <= seconds_in_simulation - 3 * 60):
                add_to_feedback("%d seconds (minute %d) elapsed in simulation" % (seconds_in_simulation, seconds_in_simulation // 60), force=True)
                self.seconds_in_simulation_last_feedback = seconds_in_simulation
            reward = GrabThePuckProblem.punishment_loss_energy # agent loses energy by default
            # Rewards associated with action I did in the past:
            # if self.apply_rewards_for_goal:
            #     add_to_feedback("APPLY REWARD FOR GOAL (cumulated reward is %.2f)" % (reward), force=True)
            #     reward = LearnToPlayHockeyProblem.REWARD_FOR_GOAL
            # elif self.apply_rewards_for_shot:
            #     add_to_feedback("APPLY REWARD FOR SHOT (cumulated reward is %.2f)" % (reward), force=True)
            #     reward = self.reward_shot
            # elif self.apply_reward_for_trying_to_shoot:
            #     sl = StraightLine.goes_by(
            #         point_1=(0, self.reward_shot),
            #         point_2=((self.hockey_world.WIDTH_HALF_ICE - self.hockey_world.GOALIE_WIDTH) / 2,
            #                  0))  # TODO: factorize this, take it out of here.
            #     dist = self.hockey_world.distance_to_closest_goal_post(self.hockey_world.puck.pos)
            #     reward = sl.apply_to(an_x=dist)
            #     add_to_feedback("Apply reward for trying to shoot: distance is %.2f feet, reward is %.2f (for an actual shot is %.2f)" % (dist, reward, self.reward_shot), force=True)
            # Rewards related to the action I did last:
            if not action_successful: # if action was unsuccessful, let's clear the deck:
                reward += self.punishment_action_failed
                add_to_feedback("Action '%s' not successful. Cumulated reward = %.2f" % (action, reward))
            else:
                if have_puck_after:
                    reward += self.reward_get_puck
                    add_to_feedback("Grabbed puck! (cumulated reward is %.2f)" % (reward), force=True)

            if self.puck_turn_idx == self.player_sensing_idx + 1:
                # ok then, move the puck! (and track goals/shots and give rewards for it)
                goals_before = self.hockey_world.goals_scored
                shots_before = self.hockey_world.shots
                behind_goal_line_before = self.hockey_world.puck.is_behind_goal_line()
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

            # has this episode finished?
            self.episode_finished = have_puck_after
            if have_puck_after:
                # Before whatever wrapping up goes on we need to record feedback:
                # self.hockey_world.datacollector.collect(self.hockey_world) # non-forcing would be: self.hockey_world.collect_data_if_is_time()
                add_to_feedback("Agent [%s] has the puck, episode finished." % (self.player_sensing.unique_id))
            if not self.feedback.is_empty():
                add_to_feedback("[action: %s]  ===============> returning reward %.2f" % (action, reward))
                print("%s" % (self.feedback))
                self.seconds_in_simulation_last_feedback = seconds_in_simulation
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
