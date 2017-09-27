from typing import Tuple, List


class StraightLine(object):

    def __init__(self, delta: float, b: float):
        self.delta = delta
        self.b = b

    @classmethod
    def goes_by(cls, point_1: Tuple[int, int], point_2: Tuple[int, int]):
        x1, y1 = point_1
        x2, y2 = point_2
        # equation from 'here' to goal:
        delta = (y2 - y1) / (x2 - x1)
        b = y1 - delta * x1
        return cls(delta=delta, b=b)

    def apply_to(self, an_x: float):
        # apply.
        return self.delta * an_x + self.b

    def cells_between(self, cell_1: Tuple[int, int], cell_2: Tuple[int, int]) -> List[Tuple[int, int]]:
        x1, y1 = cell_1
        x2, y2 = cell_2
        all_xs = list(range(x1, x2))
        all_ys = [int(self.apply_to(x)) for x in all_xs]
        return list(zip(all_xs, all_ys))

def cells_between(cell_1: Tuple[int, int], cell_2: Tuple[int, int]) -> List[Tuple[int, int]]:

    # equation from 'here' to goal:
    straight_line = StraightLine.goes_by(point_1=cell_1, point_2=cell_2)
    return straight_line.cells_between(cell_1, cell_2)
