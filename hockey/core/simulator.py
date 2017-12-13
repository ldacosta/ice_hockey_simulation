#

import abc
import pickle
import re
from mesa import Model
from pathlib import Path
import os
import time
import glob
import pandas as pd

from hockey.behaviour.core.bitstring_environment_state import BitstringEnvironmentState
from hockey.behaviour.core.hockey_scenario import LearnToPlayHockeyProblem
from typing import Optional, Tuple
import xcs
import logging
from xcs.scenarios import ScenarioObserver
import xcs.bitstrings

from util.base import find_newest_file_in_dir
import numpy as np
from geometry.point import Point
from geometry.vector import Vec2d
from hockey.behaviour.core.action import HockeyAction
from hockey.core.evaluator import Evaluator



class Simulator(metaclass=abc.ABCMeta):

    def __init__(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def is_running(self) -> bool:
        pass

class MesaModelSimulator(Simulator):

    def __init__(self, mesa_model: Model):
        Simulator.__init__(self)
        self.model = mesa_model

    def run(self):
        self.model.run_model()

    def is_running(self) -> bool:
        return self.model.running

    def step(self):
        self.model.step()

class ScenarioSimulator(Simulator):

    MODELS_DIR = "/tmp/luis/models" # TODO: change!!!!!
    os.makedirs(MODELS_DIR, exist_ok=True)

    def __init__(self,
                 xcs_scenario: LearnToPlayHockeyProblem,
                 load_from_dir_name: Optional[str],
                 load_from_file_name: Optional[str],
                 save_to_dir_name: Optional[str]):
        Simulator.__init__(self)
        self.hockey_problem = xcs_scenario
        self.running = False
        if load_from_dir_name is not None:
            if not Path(load_from_dir_name).is_dir():
                raise RuntimeError("[loading brain] '%s' is not a directory" % (load_from_dir_name))
        self.load_from_dir_name = load_from_dir_name
        self.load_from_file_name = load_from_file_name
        if load_from_dir_name is not None and load_from_file_name is not None:
            load_from = os.path.join(self.load_from_dir_name, self.load_from_file_name)
            if not Path(load_from).is_file():
                raise RuntimeError("[loading brain] File '%s' does not contain a brain" % (load_from))
        if save_to_dir_name is not None:
            if not Path(save_to_dir_name).is_dir():
                raise RuntimeError("[saving brain] '%s' is not a directory" % (save_to_dir_name))
        self.save_to_dir_name = save_to_dir_name

    def run_until_done(self):
        start_time = time.time()
        while self.hockey_problem.hockey_world.running:
            self.run()
            self.hockey_problem.reset()
            elapsed_time = time.time() - start_time
            print("run_until_done -> time so far: %.2f secs. (minute %d)" % (elapsed_time, int(elapsed_time // 60)))
        print("run_until_done -> DONE")

    def __find_newest_brain_in_dir(self, directory: str) -> Optional[str]:
        return find_newest_file_in_dir(directory, file_pattern='*.bin')

    def run(self):
        self.scenario = ScenarioObserver(self.hockey_problem)
        def show_good_rules(model):
            dict = {}
            for rule in model:
                dict[rule.action] = dict.get(rule.action, []) + [rule]
            # print("Actions: %s" %  (dict.keys()))
            dict.update((k, sorted(rule_list, key=lambda rule: rule.fitness, reverse=True)) for k, rule_list in dict.items())
            print("Best rules: (only showing actions that have rules with fitness > 0.5")
            for act, rule_list in dict.items():
                good_rules = [r for r in rule_list if r.fitness > 0.5]
                if len(good_rules) > 0:
                    print("Action %s: %d good rules: " % (act, len(good_rules)))
                    for rule in good_rules:
                        print("\t %s (fitness: %.2f, experience: %d, avg. reward: %.2f, error: %.2f)" % (rule.condition, rule.fitness, rule.experience, rule.average_reward, rule.error))

        self.running = True

        logging.root.setLevel(logging.INFO)
        algorithm = xcs.XCSAlgorithm()

        # # Default parameter settings in test()
        # algorithm.exploration_probability = .3
        # # Modified parameter settings
        # algorithm.ga_threshold = 1
        # algorithm.crossover_probability = .5
        # algorithm.do_action_set_subsumption = True
        # algorithm.do_ga_subsumption = False
        # algorithm.wildcard_probability = .998
        # algorithm.deletion_threshold = 1
        # algorithm.mutation_probability = .002



        # Use the built-in pickle module to save/reload your model for reuse.
        # import pickle
        # pickle.dump(model, open('model.bin', 'wb'))
        # reloaded_model = pickle.load(open('model.bin', 'rb'))

        # scenario = MUXProblem()
        # algorithm = XCSAlgorithm()
        # algorithm.exploration_probability = .1
        # model = algorithm.run(self.scenario)


        create_new = False
        if self.load_from_dir_name is None:
            create_new = True
        elif self.load_from_file_name is None:
            load_from = self.__find_newest_brain_in_dir(self.load_from_dir_name)
            if load_from is None:
                create_new = True
        else:
            load_from = os.path.join(self.load_from_dir_name, self.load_from_file_name)
            if not Path(load_from).is_file():
                raise RuntimeError("File '%s' does not contain a brain" % (load_from))
        if create_new:
            # Create a classifier set from the algorithm, tailored for the
            # scenario you have selected.
            print("Creating new algorithm for scenario...")
            model = algorithm.new_model(self.scenario)
        else:
            last_modified_str = time.ctime(os.stat(load_from).st_mtime)
            print("Loading model from file '%s' (last modified on %s)..." % (load_from, last_modified_str))
            model = pickle.load(open(load_from, 'rb'))
            show_good_rules(model)
        print("Loading/Creation Done")

        model.algorithm.exploration_probability = 1e-5 # .01 # .25
        model.algorithm.crossover_probability = .25
        model.algorithm.do_action_set_subsumption = True
        model.algorithm.idealization_factor = 1
        # model.algorithm.mutation_probability = .02
        # model.algorithm.discount_factor = 0.95 # 0.02 #

        # print(model.algorithm.discount_factor)
        # input("Press Enter to start simulation...")
        # Run the classifier set in the scenario, optimizing it as the
        # scenario unfolds.
        model.run(self.scenario, learn=True)

        # Get a quick list of the best classifiers discovered.
        # show_good_rules(model)

        if self.save_to_dir_name is not None:
            brain_file_name, full_brain_file_name = self.__chose_brain_file_name()
            print("Saving model into file '%s'..." % (full_brain_file_name))
            pickle.dump(model, open(full_brain_file_name, 'wb'))
            print("Saving Done")
            # set up next loading
            self.load_from_dir_name = self.save_to_dir_name
            self.load_from_file_name = brain_file_name

            brain_name, brain_ext = os.path.splitext(brain_file_name)

            eval_file_name = brain_name + ".eval"
            eval_full_file_name = os.path.join(self.save_to_dir_name, eval_file_name)
            print("Saving results of evaluation in %s" % (eval_full_file_name))
            evaluator = Evaluator(player=self.hockey_problem.hockey_world.attack[0],
                                  load_from_full_file_name=full_brain_file_name,
                                  total_number_of_actions=len(self.hockey_problem.possible_actions), steps_in_height=1, steps_in_widht=1)
            # mean_value, std_value = evaluator.quality_when_looking_at_left()
            # TODO: not result_matrix!!!!!!!
            pd.DataFrame(evaluator.result_matrix).to_csv(eval_full_file_name, header=None, index=None)
            # df = pd.read_csv(eval_file_name)
            # TODO: finish
            print("Evaluation of Brain Done")


        # steps, reward, seconds, model = xcs.test(algorithm, scenario=self.scenario) # algorithm=XCSAlgorithm,
        self.running = False

    def __chose_brain_file_name(self) -> Tuple[str, str]:
        BRAIN_FILENAME_TEMPLATE = "brain_episode_%d.bin"
        newest_brain = self.__find_newest_brain_in_dir(self.load_from_dir_name)
        if newest_brain is None:
            new_brain_idx = 1
        else:
            numbers = re.findall(r'(\d+).bin', newest_brain)
            assert len(numbers) == 1, "newest_brain = %s, but I find several numbers (%s)" % (newest_brain, numbers)
            new_brain_idx = int(numbers[0]) + 1
        brain_file_name = BRAIN_FILENAME_TEMPLATE % new_brain_idx
        full_brain_file_name = os.path.join(self.save_to_dir_name, brain_file_name)
        return brain_file_name, full_brain_file_name

    def __chose_brain_file_name2(self) -> Tuple[str, str]:
        BRAIN_FILENAME_TEMPLATE = "brain_episode_%d.bin"
        num_brain_file = 1
        brain_file_name = BRAIN_FILENAME_TEMPLATE % num_brain_file
        full_brain_file_name = os.path.join(self.save_to_dir_name, brain_file_name)
        print("[choose brain file name]...")
        while os.path.exists(full_brain_file_name):
            num_brain_file += 1
            brain_file_name = BRAIN_FILENAME_TEMPLATE % num_brain_file
            full_brain_file_name = os.path.join(self.save_to_dir_name, brain_file_name)
        print("[choose brain file name] Chose '%s'..." % (full_brain_file_name))
        return brain_file_name, full_brain_file_name

    def is_running(self) -> bool:
        return self.running
