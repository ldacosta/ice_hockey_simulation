import abc

class EnvironmentState(metaclass=abc.ABCMeta):
    """What can I sense from the environment."""

    def __init__(self, my_id: str):
        self.id = my_id
