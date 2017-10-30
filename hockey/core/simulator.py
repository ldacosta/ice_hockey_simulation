

import abc

from mesa import Model

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

    def __init__(self, xcs_scenario: Scenario):
        Simulator.__init__(self)
        self.scenario = ScenarioObserver(xcs_scenario)
        self.running = False

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


        # Create a classifier set from the algorithm, tailored for the
        # scenario you have selected.
        model = algorithm.new_model(self.scenario)

        # Run the classifier set in the scenario, optimizing it as the
        # scenario unfolds.
        model.run(self.scenario, learn=True)

        # Or get a quick list of the best classifiers discovered.
        for rule in model:
            if rule.fitness > .5 and rule.experience > 10:
                print(rule.condition, '=>', rule.action, ' [%.5f]' % rule.fitness)

        # steps, reward, seconds, model = xcs.test(algorithm, scenario=self.scenario) # algorithm=XCSAlgorithm,
        self.running = False

    def is_running(self) -> bool:
        return self.running



