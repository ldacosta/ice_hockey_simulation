#!/usr/bin/env python
"""A piece of ice.

"""

import sys

from hockey.behaviour.core.hockey_scenario import GrabThePuckProblem
from hockey.core.animation.animate_particles_on_ice import animate
from hockey.core.ice_surface.no_obstacles import Ice5x5 as NoObstacles5x5

if __name__ == "__main__":
    ice_environment = NoObstacles5x5(how_many_offense=1, how_many_defense=0)
    animate(sys.argv[1:], ice_environment, hockey_problem=GrabThePuckProblem(hockey_world=ice_environment))
