import pygame
import random
import pandas as pd
import time

from geometry.point import Point
from hockey.core.model import TIME_PER_FRAME
from hockey.behaviour.core.xcs_brain import LearnToPlayHockeyProblem
from hockey.core.simulator import Simulator, MesaModelSimulator, ScenarioSimulator
from hockey.core.half_rink import HockeyHalfRink
from hockey.visualization.pygame.half_rink import HalfRinklPygameRenderable
from pygame.color import THECOLORS

from rendering.pygame.base import pygame_render
from hockey.visualization.pygame.global_def import HALF_ICE_WIDTH, HALF_ICE_HEIGHT



if __name__ == "__main__":
    # field
    hockey_rink = HockeyHalfRink(how_many_offense=5, how_many_defense=5, one_step_in_seconds=TIME_PER_FRAME, collect_data_every_secs=1.5)

    if False:
        mesa_simulator = MesaModelSimulator(mesa_model=hockey_rink)
        hockey_problem = LearnToPlayHockeyProblem(hockey_world=hockey_rink)
        xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem)
        mesa_simulator.run()

        print("allo")

        hockey_rink.datacollector.get_model_vars_dataframe().to_csv("/tmp/model.pd")
        hockey_rink.datacollector.get_agent_vars_dataframe().to_csv("/tmp/agents.pd")

    model_df = pd.read_csv("/tmp/model.pd")
    num_steps = model_df["Unnamed: 0"].max()
    agents_df = pd.read_csv("/tmp/agents.pd")

    pygame.init()
    clock = pygame.time.Clock()
    # all renderings
    hockey_rink_renderable = HalfRinklPygameRenderable(hockey_rink)
    # Let's get ready to display:
    pygame.display.set_caption("Hockey Monster!!!!!")
    surface = pygame.display.set_mode((HALF_ICE_WIDTH, HALF_ICE_HEIGHT), 0, 32)
    surface.fill(THECOLORS['black'])

    FPS = 30

    for i in range(num_steps + 1):
        df_step = agents_df.loc[agents_df['Step'] == i]
        print("Step %d/%d" % (i, num_steps))
        defenses_seen = 0
        attackers_seen = 0
        for idx, row in df_step.iterrows():
            agent_id = row['AgentID']
            print("              " + agent_id)
            the_pos = Point(x=row['pos_x'], y=row['pos_y'])
            if agent_id.startswith("defense"):
                hockey_rink.defense[defenses_seen].pos = the_pos
                defenses_seen += 1
            elif agent_id.startswith("forward"):
                hockey_rink.attack[attackers_seen].pos = the_pos
                attackers_seen += 1
            elif agent_id.startswith("puck"):
                hockey_rink.puck.pos = the_pos
            else:
                assert False
        tick_time = clock.tick(FPS)
        surface.fill(THECOLORS['black']) # this is basically a CLEAR. TODO: can we do something better????

        pygame_render(hockey_rink_renderable.representation(), surface)
        pygame.display.update()
        time.sleep(5)



    if False:

        import sys
        import threading

        def run_in_thread(simulator: Simulator):
            threading.Thread(target=simulator.run).start()

        FPS = 30

        pygame.init()

        clock = pygame.time.Clock()
        # all renderings
        hockey_rink_renderable = HalfRinklPygameRenderable(hockey_rink)

        # Let's get ready to display:
        pygame.display.set_caption("Hockey Monster!!!!!")
        surface = pygame.display.set_mode((HALF_ICE_WIDTH, HALF_ICE_HEIGHT), 0, 32)
        surface.fill(THECOLORS['black'])

        if random.random() > 0.0: # TODO: choose somehow better
            simulator = mesa_simulator
        else:
            simulator = xcs_simulator

        run_in_thread(simulator)


        while simulator.is_running():
            tick_time = clock.tick(FPS)
            surface.fill(THECOLORS['black']) # this is basically a CLEAR. TODO: can we do something better????

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame_render(hockey_rink_renderable.representation(), surface)
            pygame.display.update()
