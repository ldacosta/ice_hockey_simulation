
import pickle
import time
import os
import random
import xcs
from pathlib import Path
from typing import Callable, Optional, Tuple, List

from hockey.core.player.base import Player
from hockey.core.half_rink import HockeyHalfRink
from hockey.behaviour.core.bitstring_environment_state import BitstringEnvironmentState

import numpy as np
from geometry.point import Point
from geometry.angle import AngleInRadians
from geometry.vector import Vec2d, X_UNIT_VECTOR
from hockey.behaviour.core.action import HockeyAction


# Diverse actions for the player to perform.

def turn_player_until(p: Player, f_cond: Callable[[AngleInRadians], bool]):
    p.looking_at = X_UNIT_VECTOR
    angle2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)
    while not f_cond(angle2puck):
        p.turn_right()
        angle2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)

def look_at_right_and_near(p: Player):
    turn_player_until(p, f_cond = lambda a: a.value >= AngleInRadians.THREE_HALFS_OF_PI)

def look_at_right_and_away(p: Player):
    turn_player_until(p, f_cond=lambda a: (a.value > AngleInRadians.PI and a.value <= AngleInRadians.THREE_HALFS_OF_PI))

def look_at_left_and_near(p: Player):
    turn_player_until(p, f_cond=lambda a: a.value <= AngleInRadians.PI_HALF)

def look_at_left_and_away(p: Player):
    turn_player_until(p, f_cond=lambda a: (a.value > AngleInRadians.PI_HALF and a.value <= AngleInRadians.PI))

# def look_at_right_and_away(p: Player):
#     p.looking_at = X_UNIT_VECTOR
#     v2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)
#     while not (v2puck > AngleInRadians.THREE_HALFS_OF_PI):
#         p.turn_right()
#         v2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)
#
# def look_at_right_and_near(p: Player):
#     p.looking_at = X_UNIT_VECTOR
#     v2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)
#     while not (v2puck > AngleInRadians.PI and v2puck < AngleInRadians.THREE_HALFS_OF_PI):
#         p.turn_right()
#         v2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)
#
# def look_at_left_and_away(p: Player):
#     p.looking_at = X_UNIT_VECTOR
#     v2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)
#     while not (v2puck < AngleInRadians.PI_HALF):
#         p.turn_right()
#         v2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)
#
# def look_at_left_and_near(p: Player):
#     p.looking_at = X_UNIT_VECTOR
#     v2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)
#     while not (v2puck > AngleInRadians.PI_HALF and v2puck < AngleInRadians.PI):
#         p.turn_right()
#         v2puck = p.model.angle_to_puck(a_pos=p.pos, looking_at=p.looking_at)

class Evaluator(object):

    def __init__(self,
                 player: Player,
                 load_from_full_file_name: str,
                 total_number_of_actions: int,
                 steps_in_height: int,
                 steps_in_widht: int):
        print("setting random")
        random.seed(333)
        if not Path(load_from_full_file_name).is_file():
            raise RuntimeError("'%s' doesn't look like a model file name" % (load_from_full_file_name))
        self.load_from = load_from_full_file_name
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
        self.sensing_matrix = None # what am I sensing at each point
        self.distance2optimal = None # the action I take: how far is it from optimal?
        world_width = self.world.width
        world_height = self.world.height
        self.heights_to_sample = list(range(0, world_height, 1))
        self.widths_to_sample = list(range(0, world_width, 1))
        self.problem_name = ""
        self.actions_on_sensing = {}
        # optimal actions
        self.optimal_actions = {}
        self.optimal_actions["look_at_right_and_away"] = (look_at_right_and_away, [HockeyAction.TURN_HARD_RIGHT])
        self.optimal_actions["look_at_right_and_near"] = (look_at_right_and_near, [HockeyAction.TURN_HARD_RIGHT, HockeyAction.SKATE_MIN_SPEED])
        self.optimal_actions["look_at_left_and_away"] = (look_at_left_and_away, [HockeyAction.TURN_HARD_LEFT])
        self.optimal_actions["look_at_left_and_near"] = (look_at_left_and_near, [HockeyAction.TURN_HARD_LEFT, HockeyAction.SKATE_MIN_SPEED])
        self.perf_matrixes = {}
        self.quality = self.update_quality() # based on how much the actions of this brain match the optimals.


    def quality_performance(self, result_matrix) -> Tuple[float, float]:
        assert result_matrix is not None
        return (np.mean(result_matrix), np.std(result_matrix))


    def warm_up(self, problem_name: str, pre_sense_fn: Callable[[Player], None], verbose: bool = False):
        assert len(problem_name) > 0
        self.problem_name = problem_name
        self.pre_sense_fn = pre_sense_fn
        print("[WARMING UP problem '%s'] sweeping ice size height = %d, width = %d..." %
              (self.problem_name, self.world.HEIGHT_ICE, self.world.WIDTH_HALF_ICE))
        for h in self.heights_to_sample:
            if verbose and h % 10 == 0:
                print("sweeping height %d out of %d" % (h, self.world.HEIGHT_ICE))
                # print("Puck position: %s" % (self.world.puck.pos))
            for w in self.widths_to_sample:
                # place agent, apply actions pre-specified
                self.world.space.place_agent(self.player, pos=Point(w, h))
                pre_sense_fn(self.player)
                assert self.player.pos == Point(w, h)
                # let's sense the environment and see what the brain says to do:
                situation_sensed = BitstringEnvironmentState(full_state=self.player.sense()).as_bitstring()
                match_set2 = self.model.match(situation_sensed)
        #         if len(match_set2) == 0:
        #             print("Nothing here!!!!")
        print("[WARMING UP] DONE")

    def __performance_matrix__(self,
                               warm_up: bool,
                               pre_sense_fn: Callable[[Player], None],
                               optimal_actions:List[HockeyAction],
                               near_optimal_actions:List[HockeyAction],
                               compare_with: Optional[Tuple[np.ndarray, np.ndarray]],
                               verbose: bool) -> np.ndarray:
        """
        bla
        Specific for:
        * attackers.
        * only changes on agent are parameters of this function.
        Args:
            self: 

        Returns:

        """
        if (warm_up):
            self.warm_up(problem_name="lalala", pre_sense_fn=pre_sense_fn, verbose=False)
            assert len(self.problem_name) > 0, "Problem not chosen (call 'warm_up' first!)"
        if (compare_with is not None):
            compare_with_values, compare_with_bitstrings = compare_with
        if (verbose):
            print("+++++++++++++++++++++++ self.model.algorithm.exploration_probability = %.2f" % (self.model.algorithm.exploration_probability))
        result_matrix = np.ones((len(self.heights_to_sample), len(self.widths_to_sample))) * -1
        # bitstring_matrix = np.ones((len(heights_to_sample), len(widths_to_sample))) * -1
        bitstring_matrix = np.empty(shape=(len(self.heights_to_sample), len(self.widths_to_sample)), dtype=object)
        #
        self.sensing_matrix = np.ones((len(self.heights_to_sample), len(self.widths_to_sample))) * -1
        self.distance2optimal = np.ones((len(self.heights_to_sample), len(self.widths_to_sample))) * -1
        # # result_matrix = np.random.random((len(heights_to_sample), len(widths_to_sample)))
        # distance_to_grab = 10
        # result_matrix[0:distance_to_grab - 1, 0:distance_to_grab - 1] = 1 # I am "just a cote" of the puck, so action by default will be 'pick up'

        self.actions_on_sensing = {}
        if (verbose):
            print("sweeping ice size height = %d, width = %d..." % (self.world.HEIGHT_ICE, self.world.WIDTH_HALF_ICE))
        for h in self.heights_to_sample:
            if verbose and h % 10 == 0:
                print("sweeping height %d out of %d" % (h, self.world.HEIGHT_ICE))
                # print("Puck position: %s" % (self.world.puck.pos))
            for w in self.widths_to_sample:
                if result_matrix[h,w] == -1:
                    # place agent, apply actions pre-specified
                    self.world.space.place_agent(self.player, pos=Point(w, h))
                    pre_sense_fn(self.player)
                    assert self.player.pos == Point(w, h)
                    # let's sense the environment and see what the brain says to do:
                    situation_sensed = BitstringEnvironmentState(full_state=self.player.sense()).as_bitstring()
                    bitstring_matrix[h,w] = situation_sensed
                    self.sensing_matrix[h, w] = hash(situation_sensed)

                    # ************************************************************
                    # ************************************************************
                    # ************************************************************
                    # Find the conditions that match against the current situation, and
                    # group them according to which action(s) they recommend.
                    by_action = {}
                    for condition, actions in self.model._population.items():
                        if not condition(situation_sensed):
                            continue

                        for action, rule in actions.items():
                            if action in by_action:
                                by_action[action][condition] = rule
                            else:
                                by_action[action] = {condition: rule}

                    # Construct the match set.
                    match_set = xcs.MatchSet(self.model, situation_sensed, by_action)
                    # ************************************************************
                    # ************************************************************
                    # ************************************************************




                    # match_set = self.model.match(situation_sensed)
                    action_sets = match_set._action_sets

                    # limit_for_choosing = self.model.algorithm.initial_prediction + abs(self.model.algorithm.initial_prediction)
                    # action_sets = { an_action: action_sets[an_action]
                    #                           for an_action in match_set._action_sets
                    #                           if abs(action_sets[an_action].prediction) > limit_for_choosing }

                    # 1 if perfect, 0: completely off.
                    dict_as_list = [[k, v] for k, v in action_sets.items()]
                    if len(dict_as_list) > 0:
                        sorted_list = sorted(dict_as_list, key=lambda ssss: ssss[1].prediction, reverse=True)
                        best_action = sorted_list[0][0]
                        # result_matrix[h, w] = hash(best_action)

                        actions_proposed = self.actions_on_sensing.get(situation_sensed, [])
                        actions_proposed = \
                            actions_proposed if len([elt for elt in actions_proposed if elt[0] == best_action]) > 0 \
                                else actions_proposed + [(best_action, 0, sorted_list)]
                        new_actions_proposed = list(map(lambda t: t if t[0] != best_action else (t[0], t[1] + 1, t[2]), actions_proposed))
                        self.actions_on_sensing[situation_sensed] = new_actions_proposed

                        result_matrix[h, w] = \
                            1 if (best_action in set(optimal_actions)) \
                                else 0.5 if (best_action in set(near_optimal_actions)) \
                                else 0
                        self.distance2optimal[h, w] = (1 if best_action in optimal_actions else -1) * \
                                                      action_sets[best_action].prediction_weight
                    else:
                        result_matrix[h, w] = 0
                        self.distance2optimal[h, w] = -0.99 # whatever. TODO?

                    # best_action = match_set.best_actions[0]

                    # import functools
                    # lll = list(map(lambda x: match_set._action_sets[x].prediction, match_set))
                    # sum_of_predictions = functools.reduce(lambda x, y: x + y, lll)
                    # def prediction_weight_or_one(an_action):
                    #     try:
                    #         return match_set._action_sets[an_action].prediction / sum_of_predictions
                    #     except Exception as e:
                    #         return 1
                    # self.distance2optimal[h, w] = min([prediction_weight_or_one(optimal_action)
                    #                                    for optimal_action in optimal_actions])





                    # deduction_units = len(set(match_set.best_actions).difference(set(optimal_actions)))
                    # deduction = deduction_units * (1 / self.total_number_of_actions)
                    # if len(match_set.best_actions) > 1:
                    #     print("\t ****** number of BEST ACTIONS = %d, so deduction is %.2f" % (len(match_set.best_actions), deduction))
                    # probably_result_of_covering = (match_set._action_sets[best_action].prediction - self.model.algorithm.initial_prediction < 1e-5)
                    # optimals_in_bests = len(set(optimal_actions).intersection(set(match_set.best_actions))) > 0
                    # result_matrix[h, w] = 1 if (best_action in set(optimal_actions)) else 0 # (1 - deduction) if optimals_in_bests else 0

                    # result_matrix[h, w] = \
                    #     0 if probably_result_of_covering \
                    #         else (1 if optimals_in_bests else 0.5)
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


        if (verbose):
            print("DONE!!!")
        assert len(np.argwhere(self.distance2optimal == -1)) == 0
        return result_matrix

    def quality_when_looking_back(self, verbose: bool = False) -> Tuple[float, float]:
        def look_back(p: Player):
            p.speed = X_UNIT_VECTOR
            p.align_with_puck()
            p.turn_left()
            p.turn_left()

        self.__performance_matrix__(
            warm_up=False,
            pre_sense_fn = look_back,
            optimal_actions=[HockeyAction.TURN_HARD_RIGHT, HockeyAction.TURN_HARD_LEFT],
            near_optimal_actions=[],
            compare_with=None,
            verbose = verbose)
        return self.quality_performance()

    def update_quality(self, verbose: bool = False) -> Tuple[float, float]:
        self.quality = (0, 0)
        self.perf_matrixes = {}
        for action_description, (movement_fn, list_of_optimals) in self.optimal_actions.items():
            perf_matrix = self.__performance_matrix__(
                warm_up=False,
                pre_sense_fn=movement_fn,
                optimal_actions=list_of_optimals,
                near_optimal_actions=[],
                compare_with=None,
                verbose=verbose)
            self.perf_matrixes[action_description] = perf_matrix
            mean_value, std_value = self.quality_performance(perf_matrix)
            if verbose:
                print("[going round a function] mean = %.2f, std-dev: %.2f" % (mean_value, std_value))
            m, s = self.quality
            self.quality = (m + mean_value, s + std_value)
        m, s = self.quality
        self.quality = (m / len(self.optimal_actions), s / len(self.optimal_actions))
        return self.quality

    def quality_when_looking_at_right_and_away_from_puck(self, verbose: bool = False) -> Tuple[float, float]:
        perf_matrix = self.__performance_matrix__(
            warm_up=False,
            pre_sense_fn = look_at_right_and_away,
            optimal_actions=[HockeyAction.TURN_HARD_RIGHT],
            near_optimal_actions=[],
            compare_with=None,
            verbose = verbose)
        return self.quality_performance(perf_matrix)

    def quality_when_looking_at_left(self, verbose: bool = False) -> Tuple[float, float]:
        def look_at_left(p: Player):
            p.speed = X_UNIT_VECTOR
            p.align_with_puck()
            p.turn_left()

        perf_matrix = self.__performance_matrix__(
            warm_up=False,
            pre_sense_fn = look_at_left,
            optimal_actions=[HockeyAction.TURN_HARD_RIGHT],
            near_optimal_actions=[],
            compare_with=None,
            verbose = verbose)
        return self.quality_performance(perf_matrix)

    def quality_when_looking_at_puck(self, verbose: bool = False) -> Tuple[float, float]:
        def look_at_puck(p: Player):
            p.speed = X_UNIT_VECTOR
            p.align_with_puck()

            perf_matrix = self.__performance_matrix__(
            warm_up=False,
            pre_sense_fn = look_at_puck,
            optimal_actions=[HockeyAction.SKATE_MIN_SPEED],
            near_optimal_actions=[],
            compare_with=None,
            verbose = verbose)
        return self.quality_performance(perf_matrix)



import matplotlib.pyplot as plt
import numpy as np
from util.base import normalize_to


def show_actions_adequacy(episode, brain_file_name, evaluator: Evaluator, height_range=None, width_range=None):
    r_matrix_looking_fwd = evaluator.result_matrix
    fig, axis = plt.subplots()
    # a = np.random.random((100, 100)) # ((16, 16))
    # plt.imshow(a, cmap='hot', interpolation='nearest')
    if height_range is None:
        height_range = slice(evaluator.sensing_matrix.shape[0])
    if width_range is None:
        width_range = slice(evaluator.sensing_matrix.shape[1])
    matrix_to_display = r_matrix_looking_fwd[width_range, height_range]
    mean_value, std_value = evaluator.quality_performance()
    # mean_value = np.mean(matrix_to_display)
    # std_value = np.std(matrix_to_display)
    heatmap = axis.pcolor(
        matrix_to_display,
        cmap=plt.cm.RdBu, vmin=0, vmax=1)  # afmhot, brg, cool or Blues)
    plt.colorbar(heatmap)
    problem_descr = "puck static at (0,0); player starts at upper right-corner"
    plt.title("Problem: %s\nEpisode: %d, Score: %.2f +/- %.2f, Source: \n'%s'" %
              (problem_descr, episode, mean_value, std_value, brain_file_name))
    plt.show()

def show_distance_to_optimal_action(episode, brain_file_name, evaluator, height_range=None, width_range=None):
    fig, axis = plt.subplots()
    # heatmap = axis.pcolor(
    #     evaluator.sensing_matrix / np.amax(evaluator.sensing_matrix),
    #     cmap=plt.cm.afmhot, vmin=0, vmax=1) # brg, cool or Blues)
    the_min = np.amin(evaluator.distance2optimal)
    the_max = np.amax(evaluator.distance2optimal)
    abs_max = max(abs(the_min), abs(the_max))
    if the_min >= 0:
        legend_min = the_min
    else:
        legend_min = -abs_max
    if the_max <= 0:
        legend_max = the_max
    else:
        legend_max = abs_max
    if height_range is None:
        height_range = slice(evaluator.sensing_matrix.shape[0])
    if width_range is None:
        width_range = slice(evaluator.sensing_matrix.shape[1])
    heatmap = axis.pcolor(
        evaluator.distance2optimal[height_range, width_range],  # .sensing_matrix, #[20:40, 0:20],
        cmap=plt.cm.RdBu, vmin=legend_min, vmax=legend_max)  # brg, cool or Blues)
    # plt.imshow(a, cmap='hot', interpolation='nearest')
    plt.colorbar(heatmap)
    problem_descr = "puck static at (0,0); player starts at upper right-corner"
    plt.title(
        "Problem: %s\nWeight of Best Action wrt Optimal Action (higher is better)\n Episode: %d, Source: \n'%s'" % (
        problem_descr, episode, brain_file_name))
    plt.show()


def show_sensings(episode, brain_file_name, evaluator, height_range=None, width_range=None):
    fig, axis = plt.subplots()

    NewRange = (1 - 0)
    OldRange = (np.amax(evaluator.sensing_matrix - np.amin(evaluator.sensing_matrix)))
    new_min = 0
    NewValue = (((evaluator.sensing_matrix - np.amin(evaluator.sensing_matrix)) * NewRange) / OldRange) + new_min

    if height_range is None:
        height_range = slice(evaluator.sensing_matrix.shape[0])
    if width_range is None:
        width_range = slice(evaluator.sensing_matrix.shape[1])
    heatmap = axis.pcolor(
        NewValue[height_range, width_range],
        # evaluator.sensing_matrix / np.amax(evaluator.sensing_matrix), #[20:40, 0:20],
        cmap=plt.cm.RdBu)  # cool) # brg, cool or Blues)
    # plt.imshow(a, cmap='hot', interpolation='nearest')
    plt.colorbar(heatmap)
    problem_descr = "puck static at (0,0); player starts at upper right-corner"
    plt.title("Problem: %s\nSensing\n Episode: %d, Source: \n'%s'" % (problem_descr, episode, brain_file_name))
    plt.show()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    from hockey.behaviour.core.hockey_scenario import GrabThePuckProblem

    plt.interactive(False)

    hockeyworld = HockeyHalfRink(how_many_defense=0, how_many_offense=1,
                                 # following parameters don't matter
                                 one_step_in_seconds=1, collect_data_every_secs=1, record_this_many_minutes=1)
    basic_fwd_problem = GrabThePuckProblem(hockeyworld)
    total_actions = len(basic_fwd_problem.get_possible_actions())
    print("total_actions = %d" % (total_actions))
    print("Starting matrix generation (looking fwd)...")
    brain_root_dir = "/Users/luisd/luis-simulation/models/speed1"
    episode = 100
    brain_file_name = os.path.join(brain_root_dir, "brain_episode_%d.bin" % (episode))
    # brain_file_name = "/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin"
    # (r_matrix_looking_fwd, bitstring_m1) = matrix_for_aligning(
    #     p=hockeyworld.attack[0],
    #     brain_file_name=brain_file_name,
    #     compare_with=None,
    #     total_actions=total_actions)
    evaluator = Evaluator(player=hockeyworld.attack[0],
                          load_from_full_file_name=brain_file_name,
                          total_number_of_actions=total_actions, steps_in_height=1, steps_in_widht=1)
    (r_matrix_looking_fwd, bitstring_m1) = matrix_for_aligning2(
        evaluator,
        False,
        compare_with=None,
        verbose=False)
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
    # fig, axis = plt.subplots()
    # # heatmap = axis.pcolor(
    # #     evaluator.distance2optimal, #.sensing_matrix, #[20:40, 0:20],
    # #     cmap=plt.cm.afmhot, vmin=0, vmax=1) # brg, cool or Blues)
    # heatmap = axis.pcolor(
    #     r_matrix_looking_fwd, #.sensing_matrix, #[20:40, 0:20],
    #     cmap=plt.cm.RdBu, vmin=0, vmax=1) # brg, cool or Blues)
    # # plt.imshow(a, cmap='hot', interpolation='nearest')
    # plt.colorbar(heatmap)
    # problem_descr = "puck static at (0,0); player starts at upper right-corner"
    # plt.title("Problem: %s\nDistance to Optimal Action\n Episode: %d, Source: \n'%s'" % (problem_descr, episode, brain_file_name))
    # plt.show()


    show_actions_adequacy(episode, brain_file_name, r_matrix_looking_fwd) # , height_range=None, width_range=None):


    print("fini!")
