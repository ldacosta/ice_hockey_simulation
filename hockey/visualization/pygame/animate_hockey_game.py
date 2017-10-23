import pygame
import random
import pandas as pd
import time
import numpy as np

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
    DATA_EVERY_SECS = TIME_PER_FRAME # .1 # 1 / 30
    RECORD_THIS_MANY_MINUTES = 60
    hockey_rink = HockeyHalfRink(how_many_offense=1, how_many_defense=0, one_step_in_seconds=TIME_PER_FRAME, collect_data_every_secs=DATA_EVERY_SECS, record_this_many_minutes=RECORD_THIS_MANY_MINUTES)

    run_simulation = True
    if run_simulation:
        mesa_simulator = MesaModelSimulator(mesa_model=hockey_rink)
        hockey_problem = LearnToPlayHockeyProblem(hockey_world=hockey_rink)
        xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem)
        # mesa_simulator.run()
        xcs_simulator.run()

        hockey_rink.datacollector.get_model_vars_dataframe().to_csv("/tmp/model.pd")
        hockey_rink.datacollector.get_agent_vars_dataframe().to_csv("/tmp/agents.pd")

    model_df = pd.read_csv("/tmp/model.pd")
    num_steps = model_df["Unnamed: 0"].max()
    num_goals = model_df["goals"].max()
    print("[Recording length: %d minutes] %d steps of simulation, %d goals" % (RECORD_THIS_MANY_MINUTES, num_steps, num_goals))
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

    DISPLAY_EVERY_SECS = .5
    steps_between_displays = round(DISPLAY_EVERY_SECS / DATA_EVERY_SECS)
    SPEED_FACTOR = -1 # -1 means: go as fast as possible!
    if SPEED_FACTOR > 0:
        total_time_between_frames = (DISPLAY_EVERY_SECS * 1000) / SPEED_FACTOR
    else:
        total_time_between_frames = 0

    times_between_frames = []
    report_every_frames = 10
    report_every_this_many_secs = 5




    for i in range(0, num_steps + 1, steps_between_displays):
        df_step = agents_df.loc[agents_df['Step'] == i]
        # print("Step %d/%d" % (i, num_steps))
        defenses_seen = 0
        attackers_seen = 0
        for idx, row in df_step.iterrows():
            agent_id = row['AgentID']
            # TODO: update speed too!
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
        tick_time = clock.tick() # (FPS)
        times_between_frames.append(tick_time)
        # print("this many: %.2f milliseconds since last update" % (tick_time))
        surface.fill(THECOLORS['black']) # this is basically a CLEAR. TODO: can we do something better????
        pygame.event.get()

        pygame_render(hockey_rink_renderable.representation(), surface)
        pygame.display.update()
        if SPEED_FACTOR > 0:
            sleep_this_much = total_time_between_frames - tick_time
            if sleep_this_much > 0:
                print("Sleeping %.2f ms., as %.2f of %.2f have already been elapsed" % (sleep_this_much, tick_time, total_time_between_frames))
                time.sleep(sleep_this_much)
        if len(times_between_frames) == report_every_frames:
            time_in_ms = np.mean(times_between_frames)
            print("Avg time (last %d frames, ~ %d seconds) between frames = %.2f ms." % (report_every_frames, report_every_this_many_secs, time_in_ms))
            report_every_frames = (1000 // time_in_ms) * report_every_this_many_secs # so I will report approx. once per second
            times_between_frames = []

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
