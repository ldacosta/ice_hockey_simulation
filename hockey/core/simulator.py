#

import abc
import pickle
from mesa import Model
from pathlib import Path
import os
import time

from hockey.behaviour.core.hockey_scenario import LearnToPlayHockeyProblem
from hockey.core.folder_manager import FolderManager
import xcs
import logging
from xcs.scenarios import ScenarioObserver
import xcs.bitstrings

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

    def __init__(self,
                 xcs_scenario: LearnToPlayHockeyProblem,
                 folder_manager: FolderManager):
        Simulator.__init__(self)
        self.hockey_problem = xcs_scenario
        self.running = False
        self.folder_manager = folder_manager

    def run_until_done(self):
        start_time = time.time()
        while self.hockey_problem.hockey_world.running:
            self.run()
            self.hockey_problem.reset()
            elapsed_time = time.time() - start_time
            print("run_until_done -> time so far: %.2f secs. (minute %d)" % (elapsed_time, int(elapsed_time // 60)))
        print("run_until_done -> DONE")

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

        load_from = self.folder_manager.newest_brain_file()
        if load_from is None:
            print("Creating new algorithm for scenario...")
            model = algorithm.new_model(self.scenario)
        else:
            if not Path(load_from).is_file():
                raise RuntimeError("File '%s' does not contain a brain" % (load_from))
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

        idx, full_brain_file_name = self.folder_manager.chose_brain_file_name()
        # brain_file_name, full_brain_file_name = self.folder_manager.chose_brain_file_name()
        print("Saving model into file '%s'..." % (full_brain_file_name))
        pickle.dump(model, open(full_brain_file_name, 'wb'))
        print("Saving Done")

        evaluator = Evaluator(player=self.hockey_problem.hockey_world.attack[0],
                              load_from_full_file_name=full_brain_file_name,
                              total_number_of_actions=len(self.hockey_problem.possible_actions), steps_in_height=1,
                              steps_in_widht=1)
        if not evaluator.save_performances_to(full_file_name=self.folder_manager.brain_eval_file_name(episode=idx, full=True)):
            print("PROBLEM saving performances to disk.")


        # for action_description, the_matrix in evaluator.perf_matrixes.items():
        #     eval_full_file_name = self.folder_manager.brain_eval_file_name(episode=idx, eval_type=action_description, full=True)
        #     print("[%s] Saving results of evaluation in %s" % (action_description, eval_full_file_name))
        #
        #     with open("dict.pickle", "wb") as pickle_out:
        #         pickle.dump(a_dict, pickle_out)
        #
        #     pd.DataFrame(the_matrix).to_csv(eval_full_file_name, header=None, index=None)
        print("Evaluation of Brain Done")

        # steps, reward, seconds, model = xcs.test(algorithm, scenario=self.scenario) # algorithm=XCSAlgorithm,
        self.running = False

    def is_running(self) -> bool:
        return self.running
