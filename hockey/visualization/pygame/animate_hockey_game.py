
import sys
import os
import pygame
import random
import pandas as pd
import time
import numpy as np

from geometry.point import Point
from geometry.vector import Vec2d
from hockey.core.model import TIME_PER_FRAME
from hockey.behaviour.core.hockey_scenario import BasicForwardProblem
from hockey.core.simulator import Simulator, MesaModelSimulator, ScenarioSimulator
from hockey.core.half_rink import HockeyHalfRink
from hockey.visualization.pygame.half_rink import HalfRinklPygameRenderable
from pygame.color import THECOLORS

from rendering.pygame.base import pygame_render
from hockey.visualization.pygame.global_def import HALF_ICE_WIDTH, HALF_ICE_HEIGHT


import sys, getopt

def main(argv):
    def show_options():
        print("To run experience, do:")
        print("> animate_hockey_game.py -s <save_every_seconds> -r <record_in_minutes> -o <output_file_name>")
        #
        print("To display results of experience, do:")
        print("> animate_hockey_game.py -d <display_every_seconds> -i <input_file_name>")
    # DATA_EVERY_SECS = 2 # TIME_PER_FRAME # .1 # 1 / 30
    # RECORD_THIS_MANY_MINUTES = 30 # 60 * 3 # 60' == 1 game

    # DISPLAY_EVERY_SECS = 5 * DATA_EVERY_SECS #5.0 # .5 #
    # assert DISPLAY_EVERY_SECS >= DATA_EVERY_SECS
    DATA_EVERY_SECS = 0
    RECORD_THIS_MANY_MINUTES = 0
    DISPLAY_EVERY_SECS = 0
    output_directory = ""
    input_directory = ""
    try:
      opts, args = getopt.getopt(argv,"hs:r:d:i:o:",["save_every_seconds=","record_in_minutes=","display_every_seconds=","input_directory=","output_directory="])
    except getopt.GetoptError:
       show_options()
       sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            show_options()
            sys.exit()
        elif opt in ("-s", "--save_every_seconds"):
            DATA_EVERY_SECS = float(arg)
        elif opt in ("-r", "--record_in_minutes"):
            RECORD_THIS_MANY_MINUTES = int(arg)
        elif opt in ("-d", "--display_every_seconds"):
            DISPLAY_EVERY_SECS = float(arg)
        elif opt in ("-o", "--output_directory"):
            output_directory = str(arg)
        elif opt in ("-i", "--input_directory"):
            input_directory = str(arg)
        else:
            print("Unrecognized option %s" % (opt))
    #
    if (DATA_EVERY_SECS > 0 and DISPLAY_EVERY_SECS > 0) or (DATA_EVERY_SECS == 0 and DISPLAY_EVERY_SECS == 0):
        show_options()
        raise RuntimeError("Either you generate data (by specifying -s and its companions) or you display data (by setting -d). You can't do both")
    mode_simulation = DATA_EVERY_SECS > 0 # otherwise in mode visualization
    if mode_simulation and DATA_EVERY_SECS <= 0:
        raise RuntimeError("[save every seconds] parameter must be > 0 (currently %.2f)" % (DATA_EVERY_SECS))
    if mode_simulation and RECORD_THIS_MANY_MINUTES <= 0:
        raise RuntimeError("[record this many minutes] parameter must be > 0 (currently %.2f)" % (RECORD_THIS_MANY_MINUTES))
    if (not mode_simulation) and DISPLAY_EVERY_SECS <= 0:
        raise RuntimeError("[display every seconds] parameter must be > 0 (currently %.2f)" % (DISPLAY_EVERY_SECS))
    if mode_simulation and output_directory == "":
        raise RuntimeError("[mode = simulation] output directory must be specified")
    if not mode_simulation and input_directory == "":
        raise RuntimeError("[mode = visualization] input directory must be specified")



    # if DATA_EVERY_SECS > DISPLAY_EVERY_SECS:
    #     raise RuntimeError("Snapshots must be saved more often than the expected visualization (currently: saving every %.2f seconds, displaying every %.2f)" % (DATA_EVERY_SECS, DISPLAY_EVERY_SECS))

    if mode_simulation:
        os.makedirs(output_directory, exist_ok=True)
        full_model_file_name = os.path.join(output_directory, "model.pd")
        agents_file_name = os.path.join(output_directory, "agents.pd")
        print("Will record %d minutes of simulated action, snapshots every %.2f seconds; will then save output in %s"
              % (RECORD_THIS_MANY_MINUTES, DATA_EVERY_SECS, output_directory))
    else:
        if not os.path.exists(input_directory):
            raise RuntimeError("Directory [%s] does not exist" % (input_directory))
        full_model_file_name = os.path.join(input_directory, "model.pd")
        agents_file_name = os.path.join(input_directory, "agents.pd")
        print("Will then visualize snapshots from [%s] separated by %.2f seconds"
              % (input_directory, DISPLAY_EVERY_SECS))

    # field
    hockey_rink = HockeyHalfRink(how_many_offense=1, how_many_defense=0, one_step_in_seconds=TIME_PER_FRAME, collect_data_every_secs=DATA_EVERY_SECS, record_this_many_minutes=RECORD_THIS_MANY_MINUTES)

    if mode_simulation:
        mesa_simulator = MesaModelSimulator(mesa_model=hockey_rink)
        hockey_problem = BasicForwardProblem(hockey_world=hockey_rink)
        xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem)
        # mesa_simulator.run()
        xcs_simulator.run()

        hockey_rink.datacollector.get_model_vars_dataframe().to_csv(full_model_file_name) # ("/tmp/model.pd")
        hockey_rink.datacollector.get_agent_vars_dataframe().to_csv(agents_file_name) # ("/tmp/agents.pd")
    else:
        model_df = pd.read_csv(full_model_file_name) # ("/tmp/model.pd")
        num_steps = model_df["Unnamed: 0"].max()
        num_goals = model_df["goals"].max()
        print("[Recording length: %d minutes] %d steps of simulation, %d goals" % (RECORD_THIS_MANY_MINUTES, num_steps, num_goals))
        DATA_EVERY_SECS = round(model_df.iloc[2]["timestamp"] - model_df.iloc[1]["timestamp"], 5)
        agents_df = pd.read_csv(agents_file_name) # ("/tmp/agents.pd")

        pygame.init()
        clock = pygame.time.Clock()
        # all renderings
        hockey_rink_renderable = HalfRinklPygameRenderable(hockey_rink)
        # Let's get ready to display:
        pygame.display.set_caption("Hockey Monster!!!!!")
        surface = pygame.display.set_mode((HALF_ICE_WIDTH, HALF_ICE_HEIGHT), 0, 32)
        surface.fill(THECOLORS['black'])

        # FPS = 30

        steps_between_displays = int(round(DISPLAY_EVERY_SECS / DATA_EVERY_SECS))
        print("I have data recorded every %.2f seconds, I want to display what happened every %.2f seconds, so I will display 1 out of %d frames" % (DATA_EVERY_SECS, DISPLAY_EVERY_SECS, steps_between_displays))
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
                the_pos = Point(x=row['pos_x'], y=row['pos_y'])
                the_speed = Point(x=row['speed_x'], y=row['speed_y'])
                v = Vec2d.origin_to(a_pt=the_speed)
                speed_angle = v.angle_with_x_axis()
                speed_amplitude = v.norm()
                if agent_id.startswith("defense"):
                    hockey_rink.defense[defenses_seen].pos = the_pos
                    hockey_rink.defense[defenses_seen].angle_looking_at = speed_angle
                    hockey_rink.defense[defenses_seen].current_speed = speed_amplitude
                    hockey_rink.defense[defenses_seen].speed = hockey_rink.defense[defenses_seen].speed_on_xy()
                    defenses_seen += 1
                elif agent_id.startswith("forward"):
                    hockey_rink.attack[attackers_seen].pos = the_pos
                    hockey_rink.attack[attackers_seen].angle_looking_at = speed_angle
                    hockey_rink.attack[attackers_seen].current_speed = speed_amplitude
                    hockey_rink.attack[attackers_seen].speed = hockey_rink.attack[attackers_seen].speed_on_xy()
                    attackers_seen += 1
                elif agent_id.startswith("puck"):
                    hockey_rink.puck.pos = the_pos
                else:
                    assert False
            tick_time = clock.tick() # (FPS)
            times_between_frames.append(tick_time)
            # print("this many: %.2f milliseconds since last update" % (tick_time))
            surface.fill(THECOLORS['black']) # this is basically a CLEAR. TODO: can we do something better????
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame_render(hockey_rink_renderable.representation(), surface)
            pygame.display.update()
            if SPEED_FACTOR > 0:
                sleep_this_much = total_time_between_frames - tick_time
                if sleep_this_much > 0:
                    print("Sleeping %.2f ms., as %.2f of %.2f have already been elapsed" % (sleep_this_much, tick_time, total_time_between_frames))
                    time.sleep(sleep_this_much)
            if len(times_between_frames) == report_every_frames:
                time_in_ms = np.mean(times_between_frames)
                print("Avg time (last %d frames, %.2f seconds in simulation time, ~ %d seconds in real time) between frames = %.2f ms." % (report_every_frames, report_every_frames * DISPLAY_EVERY_SECS, report_every_this_many_secs, time_in_ms))
                report_every_frames = (1000 // time_in_ms) * report_every_this_many_secs # so I will report approx. once per second
                times_between_frames = []


if __name__ == "__main__":
    main(sys.argv[1:])
