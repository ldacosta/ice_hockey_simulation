
import pickle
import time
import os
import random
from pathlib import Path
from typing import Callable, Optional, Tuple, List

from hockey.core.player.base import Player
from hockey.core.half_rink import HockeyHalfRink
from hockey.behaviour.core.bitstring_environment_state import BitstringEnvironmentState

import numpy as np
from geometry.point import Point
from geometry.vector import Vec2d, X_UNIT_VECTOR
from hockey.behaviour.core.action import HockeyAction


class Evaluator(object):

    def __init__(self, player: Player, load_from_full_file_name: str, total_number_of_actions: int):
        if Path(load_from_full_file_name).is_file():
            self.load_from = load_from_full_file_name
        else:
            raise RuntimeError("'%s' doesn't look like a model file name" % (load_from_full_file_name))
        self.player = player
        self.world = self.player.model
        last_modified_str = time.ctime(os.stat(self.load_from).st_mtime)
        print("Loading model from file '%s' (last modified on %s)..." % (self.load_from, last_modified_str))
        self.model = None
        with open(self.load_from, 'rb') as f:
            self.model = pickle.load(f)
        self.model.algorithm.exploration_probability = 0
        # self.model.algorithm
        self.total_number_of_actions = total_number_of_actions
        assert self.total_number_of_actions > 0

    def evaluation_matrix(self,
                          pre_sense_fn: Callable[[Player], None],
                          optimal_actions:List[HockeyAction], compare_with: Optional[Tuple[np.ndarray, np.ndarray]]) -> Tuple[np.ndarray, np.ndarray]:
        """
        bla
        Specific for:
        * attackers.
        * only changes on agent are parameters of this function.
        Args:
            self: 

        Returns:

        """
        random.seed(333)
        if (compare_with is not None):
            compare_with_values, compare_with_bitstrings = compare_with
        print("+++++++++++++++++++++++ self.model.algorithm.exploration_probability = %.2f" % (self.model.algorithm.exploration_probability))
        world_width = self.world.WIDTH_HALF_ICE
        world_height = self.world.HEIGHT_ICE
        heights_to_sample = list(range(0, world_height, 1))
        widths_to_sample = list(range(0, world_width, 1))
        result_matrix = np.ones((len(heights_to_sample), len(widths_to_sample))) * -1
        # bitstring_matrix = np.ones((len(heights_to_sample), len(widths_to_sample))) * -1
        bitstring_matrix = np.empty(shape=(len(heights_to_sample), len(widths_to_sample)), dtype=object)
        # # result_matrix = np.random.random((len(heights_to_sample), len(widths_to_sample)))
        # distance_to_grab = 10
        # result_matrix[0:distance_to_grab - 1, 0:distance_to_grab - 1] = 1 # I am "just a cote" of the puck, so action by default will be 'pick up'
        for h in heights_to_sample:
            if h % 10 == 0:
                print("sweeping height %d out of %d" % (h, world_height))
                # print("Puck position: %s" % (self.world.puck.pos))
            for w in widths_to_sample:
                if result_matrix[h,w] == -1:
                    # place agent, apply actions pre-specified
                    self.world.space.place_agent(self.player, pos=Point(w, h))
                    pre_sense_fn(self.player)
                    assert self.player.pos == Point(w, h)
                    # let's sense the environment and see what the brain says to do:
                    situation_sensed = BitstringEnvironmentState(full_state=self.player.sense()).as_bitstring()
                    bitstring_matrix[h,w] = situation_sensed
                    match_set = self.model.match(situation_sensed)
                    # 1 if perfect, 0: completely off.
                    best_action = match_set.best_actions[0]
                    deduction_units = len(set(match_set.best_actions).difference(set(optimal_actions)))
                    deduction = deduction_units * (1 / self.total_number_of_actions)

                    # if len(match_set.best_actions) > 1:
                    #     print("\t ****** number of BEST ACTIONS = %d, so deduction is %.2f" % (len(match_set.best_actions), deduction))
                    probably_result_of_covering = (match_set._action_sets[best_action].prediction - self.model.algorithm.initial_prediction < 1e-5)
                    optimals_in_bests = len(set(optimal_actions).intersection(set(match_set.best_actions))) > 0
                    result_matrix[h, w] = (1 - deduction) if optimals_in_bests else 0
                    # result_matrix[h, w] = \
                    #     0 if probably_result_of_covering \
                    #         else (1 - deduction if optimals_in_bests else 0.5)
                    if (compare_with is not None) and (compare_with_values[h,w] != result_matrix[h,w]):
                        print("At [%d,%d]: result differs! (now %.2f, before %.2f)" % (h, w, result_matrix[h,w], compare_with_values[h,w]))
                        situation_sensed_before = compare_with_bitstrings[h,w]
                        if situation_sensed == situation_sensed_before:
                            print("\t BUT sensing is the same (%s)!!!!" % (situation_sensed))
                        else:
                            print("\t situation_sensed =        %s" % (situation_sensed))
                            print("\t situation_sensed BEFORE = %s" % (situation_sensed_before))
                        if len(match_set.best_actions) > 1:
                            print("\t ****** number of BEST ACTIONS = %d" % (len(match_set.best_actions)))

        return (result_matrix, bitstring_matrix)



def matrix_for_looking_back(p: Player, brain_file_name: str, total_actions: int):
    # quick demo
    def look_back(p: Player):
        p.speed = X_UNIT_VECTOR
        p.align_with_puck()
        p.turn_left()
        p.turn_left()

    evaluator = Evaluator(player=p, load_from_full_file_name=brain_file_name, total_number_of_actions=total_actions)
    return evaluator.evaluation_matrix(pre_sense_fn=look_back,
                                           optimal_actions=[HockeyAction.TURN_HARD_RIGHT, HockeyAction.TURN_HARD_LEFT],
                                           compare_with=None)

def matrix_for_looking_at_right(p: Player, brain_file_name: str, total_actions: int):
    def look_at_right(p: Player):
        p.speed = X_UNIT_VECTOR
        p.align_with_puck()
        p.turn_right()

    evaluator = Evaluator(player=p, load_from_full_file_name=brain_file_name, total_number_of_actions=total_actions)
    return evaluator.evaluation_matrix(pre_sense_fn=look_at_right,
                                       optimal_actions=[HockeyAction.TURN_HARD_LEFT], compare_with=None)

def matrix_for_looking_at_left(p: Player, brain_file_name: str, total_actions: int):
    # quick demo
    def look_at_left(p: Player):
        p.speed = X_UNIT_VECTOR
        p.align_with_puck()
        p.turn_left()

    evaluator = Evaluator(player=p, load_from_full_file_name=brain_file_name, total_number_of_actions=total_actions)
    return evaluator.evaluation_matrix(pre_sense_fn=look_at_left,
                                       optimal_actions=[HockeyAction.TURN_HARD_RIGHT], compare_with=None)

def matrix_for_aligning(p: Player, brain_file_name: str, compare_with: Optional[np.ndarray], total_actions: int):
    # quick demo
    def look_at_puck(p: Player):
        p.speed = X_UNIT_VECTOR
        p.align_with_puck()

    evaluator = Evaluator(player=p, load_from_full_file_name=brain_file_name, total_number_of_actions=total_actions)
    return evaluator.evaluation_matrix(pre_sense_fn=look_at_puck,
                                           optimal_actions=[HockeyAction.SKATE_MIN_SPEED], compare_with=compare_with)


if __name__ == "__main__":
    from hockey.behaviour.core.hockey_scenario import GrabThePuckProblem

    hockeyworld = HockeyHalfRink(how_many_defense=0, how_many_offense=1,
                                 # following parameters don't matter
                                 one_step_in_seconds=1, collect_data_every_secs=1, record_this_many_minutes=1)
    basic_fwd_problem = GrabThePuckProblem(hockeyworld)
    total_actions = len(basic_fwd_problem.get_possible_actions())
    print("total_actions = %d" % (total_actions))
    print("Starting matrix generation (looking fwd)...")
    (r_matrix_looking_fwd, bitstring_m1) = matrix_for_aligning(
        p=hockeyworld.attack[0],
        brain_file_name="/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin",
        compare_with=None,
        total_actions=total_actions)
    # # random.seed(333)
    # (r_matrix_looking_fwd2, bitstring_m2) = matrix_for_aligning(
    #     p=hockeyworld.attack[0],
    #     brain_file_name="/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin",
    #     compare_with=(r_matrix_looking_fwd, bitstring_m1),
    #     total_actions=total_actions)
    # print("Starting matrix generation (looking LEFT)...")
    # r_matrix_looking_left,_ = matrix_for_looking_at_left(
    #     p=hockeyworld.attack[0],
    #     brain_file_name = "/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin",
    #     total_actions=total_actions)
    # print("Starting matrix generation (looking BACK)...")
    # r_matrix_looking_back, _ = matrix_for_looking_back(
    #     p=hockeyworld.attack[0],
    #     brain_file_name="/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin",
    #     total_actions=total_actions)
    print("DONE matrix generation")
