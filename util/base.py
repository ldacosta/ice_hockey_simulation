def normalize_to(a_value: float, new_min: float, new_max: float, old_min: float, old_max: float) -> float:
    OldRange = (old_max - old_min)
    if (OldRange == 0):
        NewValue = new_min
    else:
        NewRange = (new_max - new_min)
        NewValue = (((a_value - old_min) * NewRange) / OldRange) + new_min
    return NewValue

