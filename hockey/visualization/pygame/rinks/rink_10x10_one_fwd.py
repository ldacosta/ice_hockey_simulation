
import sys

from hockey.core.ice_surface.no_obstacles import IceNxN
from hockey.visualization.pygame.skating_rink import SkatingRinklPygameRenderable
from hockey.visualization.pygame.visualize_particles_on_ice import visualize

if __name__ == "__main__":
    skating_ice = IceNxN(width=10, height=10, how_many_offense=1, how_many_defense=0)
    rendr = SkatingRinklPygameRenderable(ice_rink=skating_ice)
    visualize(sys.argv[1:], ice_environment = skating_ice, renderable_ice=rendr)
