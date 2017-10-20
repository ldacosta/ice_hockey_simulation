

import abc

from mesa import Model

import xcs
from xcs.scenarios import Scenario
from xcs import XCSAlgorithm


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
        self.scenario = xcs_scenario
        self.running = False

    def run(self):
        self.running = True
        steps, reward, seconds, model = xcs.test(scenario=self.scenario) # algorithm=XCSAlgorithm,
        self.running = False

    def is_running(self) -> bool:
        return self.running



