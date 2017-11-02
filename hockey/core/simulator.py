

import abc
import pickle
from mesa import Model
from pathlib import Path
import os

from typing import Optional
import xcs
from xcs.scenarios import Scenario
from xcs import XCSAlgorithm
import logging
from xcs import XCSAlgorithm
from xcs.scenarios import MUXProblem, ScenarioObserver

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

    def __init__(self, xcs_scenario: Scenario, load_from_file_name: Optional[str], save_to_file_name: Optional[str]):
        Simulator.__init__(self)
        self.scenario = ScenarioObserver(xcs_scenario)
        self.running = False
        if load_from_file_name is None:
            self.load_from = None
        else:
            self.load_from = os.path.join(ScenarioSimulator.MODELS_DIR, load_from_file_name)
        if save_to_file_name is None:
            self.save_to = None
        else:
            self.save_to = os.path.join(ScenarioSimulator.MODELS_DIR, save_to_file_name)

    def run(self):
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

        if (self.load_from is not None) and Path(self.load_from).is_file():
            print("Loading model from file '%s'..." % (self.load_from))
            model = pickle.load(open(self.load_from, 'rb'))
        else:
            if self.load_from is not None:
                print("File '%s' does not exist." % (self.load_from))
            # Create a classifier set from the algorithm, tailored for the
            # scenario you have selected.
            print("Creating new algorithm for scenario...")
            model = algorithm.new_model(self.scenario)
        print("Done")

        # Run the classifier set in the scenario, optimizing it as the
        # scenario unfolds.
        model.run(self.scenario, learn=True)

        # Get a quick list of the best classifiers discovered.
        good_rules = 0
        for rule in model:
            if rule.fitness > .5 and rule.experience > 10:
                good_rules += 1
                print(rule.condition, '=>', rule.action, ' [%.5f, experience: %d]' % (rule.fitness, rule.experience))
            if good_rules < 2:
                if rule.fitness > .5:
                    good_rules += 1
                    print(rule.condition, '=>', rule.action, ' [%.5f]' % rule.fitness)
        if good_rules < 5:
            print("Only %d 'good' rules found" % good_rules)

        if (self.save_to is not None):
            print("Saving model into file '%s'..." % (self.save_to))
            pickle.dump(model, open(self.save_to, 'wb'))
            print("Done")

        # steps, reward, seconds, model = xcs.test(algorithm, scenario=self.scenario) # algorithm=XCSAlgorithm,
        self.running = False

    def is_running(self) -> bool:
        return self.running



