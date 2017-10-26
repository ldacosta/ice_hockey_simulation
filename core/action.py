
from enum import Enum, auto

class Action(Enum):
    """
    An action on an environment.
    Warnings:
        This class extends Enum but does not define any value,
        so specific actions for specific environments can be extended out of
        this (Python does not allow "normal" extension of Enums).
    """

    """"""

    def describe(self):
        return self.name, self.value

    def __str__(self):
        return 'Action {0}'.format(self.describe())
