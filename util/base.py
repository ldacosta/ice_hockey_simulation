import random
from typing import List
import numpy as np

def normalize_to(a_value: float, new_min: float, new_max: float, old_min: float, old_max: float) -> float:
    OldRange = (old_max - old_min)
    if (OldRange == 0):
        NewValue = new_min
    else:
        NewRange = (new_max - new_min)
        NewValue = (((a_value - old_min) * NewRange) / OldRange) + new_min
    return NewValue


def choose_by_roulette(weights: List[float]) -> int:
    """
    Chooses randomly with weights expressed in array.
    Args:
        weights: positive numbers indicating weights of each option.

    Returns:
        the index of the option chosen.

    """

    weights_as_array = np.asarray(weights)
    assert (not np.any(weights_as_array < 0))
    weights_as_probs = np.cumsum(weights_as_array) / np.sum(weights_as_array)
    r = random.random()
    for i, prob in enumerate(weights_as_probs):
        if r <= prob:
            return i
    # if it gets here we have a bug:
    raise RuntimeError("How come we got here?????")

def choose_first_option_by_roulette(weight_1: float, weight_2: float) -> bool:
    """
    Chooses randomly with weights expressed in array.
    Args:
        weight_1: weight for first option.
        weight_2: weight for second option.

    Returns:
        True if first option is the chosen. False otherwise.
    """
    return choose_by_roulette(weights = [weight_1, weight_2]) == 0
