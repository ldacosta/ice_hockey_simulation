import pygame
from hockey.core.half_rink import HockeyHalfRink
from hockey.visualization.pygame.half_rink import HalfRinklPygameRenderable
from pygame.color import THECOLORS

from rendering.pygame.base import pygame_render
from hockey.visualization.pygame.global_def import HALF_ICE_WIDTH, HALF_ICE_HEIGHT

if __name__ == "__main__":
    import sys

    FPS = 30

    pygame.init()

    clock = pygame.time.Clock()
    # field
    hockey_rink = HockeyHalfRink(how_many_offense=5, how_many_defense=5)
    # all renderings
    hockey_rink_renderable = HalfRinklPygameRenderable(hockey_rink)

    # Let's get ready to display:
    pygame.display.set_caption("Hockey Monster!!!!!")
    surface = pygame.display.set_mode((HALF_ICE_WIDTH, HALF_ICE_HEIGHT), 0, 32)

    while True:
        tick_time = clock.tick(FPS)
        surface.fill(THECOLORS['black']) # this is basically a CLEAR. TODO: can we do something better????

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        hockey_rink.step()
        pygame_render(hockey_rink_renderable.representation(), surface)
        pygame.display.update()
