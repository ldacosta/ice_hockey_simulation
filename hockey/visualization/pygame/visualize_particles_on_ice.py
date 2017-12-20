import getopt
import os
import sys
import time

import pygame
from geometry.point import Point
from geometry.vector import Vec2d
from pygame.color import THECOLORS
from rendering.pygame.base import pygame_render, Renderable

from util.base import read_and_merge_dataframes

from hockey.core.ice_surface.ice_rink import SkatingIce
from hockey.core.folder_manager import FolderManager
from hockey.core.ice_surface.no_obstacles import Ice5x5 as NoObstacles5x5
from hockey.visualization.pygame.global_def import HALF_ICE_WIDTH, HALF_ICE_HEIGHT
from hockey.visualization.pygame.half_rink import HalfRinklPygameRenderable
from hockey.visualization.pygame.skating_rink import SkatingRinklPygameRenderable

def show_options():
    print("To display results of experience, do:")
    print("> animate_particles_on_ice.py  -d <experiments_root_dir> -e <experiment_name> -a <speedup>")

def visualize(argv, ice_environment: SkatingIce, renderable_ice: Renderable):
    speedup = 0
    experiment_name = None
    all_experiments_root_dir = None
    try:
      opts, args = getopt.getopt(argv,
                                 "ha:d:e:",
                                 ["acceleration=",
                                  "experiments_root_dir=",
                                  "experiment_name=",
                                  ]
                                 )
    except getopt.GetoptError:
        print("Your command line contains options that are invalid.")
        show_options()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            show_options()
            sys.exit()
        elif opt in ("-a", "--acceleration"):
            speedup = float(arg)
        elif opt in ("-d", "--experiments_root_dir="):
            all_experiments_root_dir = str(arg)
        elif opt in ("-e", "--experiment_name="):
            experiment_name = str(arg)
        else:
            print("Unrecognized option %s" % (opt))
    #
    # if (DATA_EVERY_SECS != float("inf") and (speedup != 0)) or (DATA_EVERY_SECS == float("inf") and (speedup == 0)):
    #     show_options()
    #     raise RuntimeError("Either you generate data (by specifying -s and its companions) or you display data (by setting -d). You can't do both") # TODO: revise this message
    if (all_experiments_root_dir is None) or (experiment_name is None):
        show_options()
        raise RuntimeError("Both the root of the experiments and the experiment name has to be specified.")
    folder_manager = FolderManager(experiments_root_dir=all_experiments_root_dir, experiment_name=experiment_name)
    if not os.path.exists(folder_manager.model_dir):
        raise RuntimeError("Directory with model ('%s') does not exist" % (folder_manager.model_dir))
    if not os.path.exists(folder_manager.agents_dir):
        raise RuntimeError("Directory with agents ('%s') does not exist" % (folder_manager.agents_dir))
    if speedup <= 0:
        raise RuntimeError("[mode = visualization] input directory must be specified")

    # all model files, concatenated
    model_df = read_and_merge_dataframes(folder_manager.model_dir, prefix_fname="", verbose=True)
    # num_steps = model_df["steps"].max()
    # num_goals = model_df["goals"].max()
    # print("[Recording length: %d minutes] %d steps of simulation, %d goals" % (RECORD_THIS_MANY_MINUTES, num_steps, num_goals))
    DATA_EVERY_SECS = round(model_df.iloc[2]["timestamp"] - model_df.iloc[1]["timestamp"], 5)
    # all agent files, concatenated
    agents_df = read_and_merge_dataframes(folder_manager.agents_dir, prefix_fname="", verbose=True)
    print("Will visualize snapshots from agents at '%s' at a speedup of %.2f"
          % (folder_manager.agents_dir, speedup))

    # Let's get ready to display:
    pygame.display.set_caption("Hockey Monster!!!!!")
    surface = pygame.display.set_mode((HALF_ICE_WIDTH, HALF_ICE_HEIGHT), 0, 32)
    surface.fill(THECOLORS['black'])

    total_time_between_frames_in_ms = (DATA_EVERY_SECS * 1000) / speedup
    print("Data recorded every %.2f secs., speedup of visualization is %.2f, so frames will be separated by %.2f ms." % (DATA_EVERY_SECS, speedup, total_time_between_frames_in_ms))
    FPS = int(round(1000 * 1/total_time_between_frames_in_ms))
    print("Which means I won't share more than %d frames per second" % (FPS))
    times_between_frames = []

    pygame.init()
    clock = pygame.time.Clock()
    old_minutes_in_simulation = -1
    for curr_timestamp in list(model_df['timestamp']):
    # for i in range(0, num_steps):
        # df_step = agents_df.loc[agents_df['Step'] == i]
        df_step = agents_df.loc[agents_df['timestamp'] == curr_timestamp]
        defenses_seen = 0
        attackers_seen = 0
        for idx, row in df_step.iterrows():
            agent_id = row['AgentID']
            the_pos = Point(x=row['pos_x'], y=row['pos_y'])
            the_speed = Point(x=row['speed_x'], y=row['speed_y'])
            v = Vec2d.origin_to(a_pt=the_speed)
            speed_angle = v.angle_with_positive_x_axis()
            speed_amplitude = v.norm()
            if agent_id.startswith("defense"):
                ice_environment.defense[defenses_seen].pos = the_pos
                ice_environment.defense[defenses_seen].__set_gaze_and_speed_from__(an_angle_opt=speed_angle, a_speed_opt=speed_amplitude)
                # hockey_rink.defense[defenses_seen].angle_looking_at = speed_angle
                # hockey_rink.defense[defenses_seen].current_speed = speed_amplitude
                # hockey_rink.defense[defenses_seen].speed = hockey_rink.defense[defenses_seen].speed_on_xy()
                defenses_seen += 1
            elif agent_id.startswith("forward"):
                try:
                    ice_environment.attack[attackers_seen].pos = the_pos
                except Exception as e:
                    print("Exception of timestamp %d: %s" % (curr_timestamp, e))
                    print("attackers_seen = %d, len(hockey_rink.attack) = %d" % (attackers_seen, len(ice_environment.attack)))
                ice_environment.attack[defenses_seen].__set_gaze_and_speed_from__(an_angle_opt=speed_angle, a_speed_opt=speed_amplitude)
                # hockey_rink.attack[attackers_seen].angle_looking_at = speed_angle
                # hockey_rink.attack[attackers_seen].current_speed = speed_amplitude
                # hockey_rink.attack[attackers_seen].speed = hockey_rink.attack[attackers_seen].speed_on_xy()
                attackers_seen += 1
            elif agent_id.startswith("puck"):
                ice_environment.puck.pos = the_pos
            else:
                assert False
        # seconds_in_simulation = DATA_EVERY_SECS * i
        seconds_in_simulation = curr_timestamp
        minutes_in_simulation = seconds_in_simulation // 60
        if False: # minutes_in_simulation > old_minutes_in_simulation:
            print("[%s] Minute %d of simulation" % (time.ctime(), minutes_in_simulation))
            old_minutes_in_simulation = minutes_in_simulation
        tick_time = clock.tick(FPS)
        times_between_frames.append(tick_time)
        surface.fill(THECOLORS['black']) # this is basically a CLEAR. TODO: can we do something better????
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame_render(renderable_ice.representation(), surface)
        pygame.display.update()

if __name__ == "__main__":
    skating_ice = NoObstacles5x5(how_many_offense=1, how_many_defense=0)
    rendr = SkatingRinklPygameRenderable(ice_rink=skating_ice)
    visualize(sys.argv[1:], ice_environment = skating_ice, renderable_ice=rendr)
