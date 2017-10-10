
import abc
from core.environment_state import EnvironmentState
from core.action import Action

class Environment(metaclass=abc.ABCMeta):
    """An environment is something I can sense and I can act on."""

    def __init__(self):
        pass


class Sensor(metaclass=abc.ABCMeta):

    def __init__(self, environment: Environment):
        self.environment = environment

    @abc.abstractmethod
    def sense(self) -> EnvironmentState:
        pass

