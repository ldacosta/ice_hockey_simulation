import numpy as np
from util.base import INCHES_IN_FOOT
from geometry.vector import Vec2d
from hockey.core.object_on_ice import ObjectOnIce

class Puck(ObjectOnIce):
    """How does a Puck behave?"""

    KINETIC_FRICTION_COEF = 0.15 # from https://hypertextbook.com/facts/2004/GennaAbleman.shtml

    # Elasticity represents the loss of speed a particle experiences when it hits a boundary.
    ELASTICITY = 0.77 # inspired by http://www.petercollingridge.co.uk/book/export/html/6

    def __init__(self, hockey_world_model):
        # initially, the puck goes around randomly at low speed
        speeds = tuple(np.random.normal(loc=0.0, scale=5.0, size=2))
        self.radius = (3 * 1/INCHES_IN_FOOT)/2 # 3 inches of diameter, this many feet
        super().__init__("puck",
                         hockey_world_model,
                         size=self.radius,
                         pos_opt=None,
                         speed_opt=Vec2d(speeds))
        self.is_taken = False
        self.prob_of_goal = 0.0 # If this puck where to end up in the goal, what is the probability that it would be a goal?

    def __setattr__(self, name, value):
        if name == "prob_of_goal":
            if name in self.__dict__:
                if (self.__dict__[name] != value):
                    print("Changing value of '%s' from %.2f to %.2f" % (name, self.__dict__[name], value))
        self.__dict__[name] = value

    def move_around(self):
        self.move_by_bouncing_from_walls(
            prob_of_score_on_goal_opt=self.prob_of_goal,
            friction_constant_opt=Puck.KINETIC_FRICTION_COEF
        )

    def set_free(self):
        self.is_taken = False
        # self.prob_of_goal = 0.0

    def step(self):
        # if the puck is taken it will move with the carrier
        if not self.is_taken:
            self.move_around()
