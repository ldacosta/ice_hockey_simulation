import unittest
import os
import numpy as np

from hockey.core.half_rink import HockeyHalfRink
from hockey.behaviour.core.hockey_scenario import GrabThePuckProblem
from hockey.core.evaluator import Evaluator


class TestEvaluator(unittest.TestCase):
    """Testing definitions of a half-ice rink."""

    def setUp(self):
        """Initialization"""
        self.hockeyworld = HockeyHalfRink(width=HockeyHalfRink.WIDTH_HALF_ICE, height=HockeyHalfRink.HEIGHT_ICE, how_many_defense=0, how_many_offense=1,
                                     # following parameters don't matter
                                     one_step_in_seconds=1, collect_data_every_secs=1, record_this_many_minutes=1)
        self.basic_fwd_problem = GrabThePuckProblem(self.hockeyworld)
        self.total_actions = len(self.basic_fwd_problem.get_possible_actions())
        print("total_actions = %d" % (self.total_actions))

    def test_all_sane(self):
        """Simple 'static' check-up"""

        print("Starting matrix generation (looking fwd)...")
        brain_root_dir = "/Users/luisd/luis-simulation/models/speed1_small"
        episode = 100
        brain_file_name = os.path.join(brain_root_dir, "brain_episode_%d.bin" % (episode))
        # brain_file_name = "/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin"
        # (r_matrix_looking_fwd, bitstring_m1) = matrix_for_aligning(
        #     p=hockeyworld.attack[0],
        #     brain_file_name=brain_file_name,
        #     compare_with=None,
        #     total_actions=total_actions)
        evaluator = Evaluator(player=self.hockeyworld.attack[0],
                              load_from_full_file_name=brain_file_name,
                              total_number_of_actions=self.total_actions, steps_in_height=1, steps_in_widht=1)
        mean_value, std_value = evaluator.quality_when_looking_at_puck()
        print("[looking at puck] mean = %.2f, std-dev: %.2f" % (mean_value, std_value))

        # (r_matrix_looking_fwd, bitstring_m1) = matrix_for_aligning2(
        #     evaluator,
        #     False,
        #     compare_with=None,
        #     verbose=False)
        # # # random.seed(333)
        # # (r_matrix_looking_fwd2, bitstring_m2) = matrix_for_aligning(
        # #     p=hockeyworld.attack[0],
        # #     brain_file_name="/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin",
        # #     compare_with=(r_matrix_looking_fwd, bitstring_m1),
        # #     total_actions=total_actions)
        # # print("Starting matrix generation (looking LEFT)...")
        # # r_matrix_looking_left,_ = matrix_for_looking_at_left(
        # #     p=hockeyworld.attack[0],
        # #     brain_file_name = "/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin",
        # #     total_actions=total_actions)
        # # print("Starting matrix generation (looking BACK)...")
        # # r_matrix_looking_back, _ = matrix_for_looking_back(
        # #     p=hockeyworld.attack[0],
        # #     brain_file_name="/Users/luisd/luis-simulation/models/brainfetchpuck_onlyspeed1.bin",
        # #     total_actions=total_actions)
        # print("DONE matrix generation")
        # # fig, axis = plt.subplots()
        # # # heatmap = axis.pcolor(
        # # #     evaluator.distance2optimal, #.sensing_matrix, #[20:40, 0:20],
        # # #     cmap=plt.cm.afmhot, vmin=0, vmax=1) # brg, cool or Blues)
        # # heatmap = axis.pcolor(
        # #     r_matrix_looking_fwd, #.sensing_matrix, #[20:40, 0:20],
        # #     cmap=plt.cm.RdBu, vmin=0, vmax=1) # brg, cool or Blues)
        # # # plt.imshow(a, cmap='hot', interpolation='nearest')
        # # plt.colorbar(heatmap)
        # # problem_descr = "puck static at (0,0); player starts at upper right-corner"
        # # plt.title("Problem: %s\nDistance to Optimal Action\n Episode: %d, Source: \n'%s'" % (problem_descr, episode, brain_file_name))
        # # plt.show()
        #
        #
        # show_actions_adequacy(episode, brain_file_name, r_matrix_looking_fwd) # , height_range=None, width_range=None):
        #
        #
        # print("fini!")

