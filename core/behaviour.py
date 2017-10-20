

import abc
from typing import List
from core.environment_state import EnvironmentState
from core.action import Action

class Brain(metaclass=abc.ABCMeta):
    """An agent that acts on the environment."""

    def __init__(self):
        pass

    @abc.abstractmethod
    def propose_actions(self, the_state: EnvironmentState) -> List[Action]:
        raise NotImplementedError()
