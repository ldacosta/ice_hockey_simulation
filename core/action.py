
import abc

from enum import Enum, auto

class Action(Enum):
    """An action on an environment."""

    def describe(self):
        return self.name, self.value

    def __str__(self):
        return 'Action {0}'.format(self.describe())

# class Action(metaclass=abc.ABCMeta):
#     """An action on an environment."""
#
#     def __init__(self):
#         pass
