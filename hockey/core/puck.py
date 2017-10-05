import numpy as np
from geometry.vector import Vec2d
from hockey.core.object_on_ice import ObjectOnIce

class Puck(ObjectOnIce):
    """How does a Puck behave?"""

    def __init__(self, hockey_world_model):
        # initially, the puck goes around randomly at low speed
        speeds = tuple(np.random.normal(loc=0.0, scale=5.0, size=2))
        self.radius = (3 * 0.0834)/2 # 3 inches of diameter, this many feet
        super().__init__("puck",
                         hockey_world_model,
                         size=self.radius,
                         pos_opt=None,
                         speed_opt=Vec2d(speeds))
        self.is_taken = False

    def move_around(self):
        self.move_by_bouncing_from_walls()

    def step(self):
        # if the puck is taken it will move with the carrier
        if not self.is_taken:
            self.move_around()
