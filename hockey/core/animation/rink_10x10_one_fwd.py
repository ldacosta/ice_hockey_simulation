#!/usr/bin/env python
"""A piece of ice.

"""

import sys

from hockey.behaviour.core.hockey_scenario import GrabThePuckProblem
from hockey.core.animation.animate_particles_on_ice import animate
from hockey.core.ice_surface.no_obstacles import IceNxN

if __name__ == "__main__":
    ice_environment = IceNxN(width=10,height=10, how_many_offense=1, how_many_defense=0)
    animate(sys.argv[1:], ice_environment, hockey_problem=GrabThePuckProblem(hockey_world=ice_environment))
