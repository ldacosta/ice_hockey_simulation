import getopt
import os
import sys
import time

import pandas as pd
import pygame
from geometry.point import Point
from geometry.vector import Vec2d
from pygame.color import THECOLORS
from rendering.pygame.base import pygame_render
from typing import Optional

from hockey.behaviour.core.hockey_scenario import GrabThePuckProblem
from hockey.core.folder_manager import FolderManager
from hockey.core.half_rink import HockeyHalfRink
from hockey.core.model import TIME_PER_FRAME
from hockey.core.simulator import MesaModelSimulator, ScenarioSimulator
from hockey.visualization.pygame.global_def import HALF_ICE_WIDTH, HALF_ICE_HEIGHT
from hockey.visualization.pygame.half_rink import HalfRinklPygameRenderable
from util.base import find_newest_file_in_dir


def read_and_merge_dataframes(input_directory, prefix_fname: str, verbose: bool = False) -> pd.DataFrame:
    all_fnames = [os.path.join(input_directory, fname)
                        for fname in os.listdir(input_directory) if fname.startswith(prefix_fname) and fname.endswith(".pd")]
    if verbose:
        print("From '%s' I read %s" % (input_directory, all_fnames))
    return pd.concat(list(map(pd.read_csv, all_fnames)), ignore_index=True)


def newest_brain_in_dir(directory: str) -> Optional[str]:
    """Gets newest brain in a folder - None is there is nothing there or the directory doesn't exist."""
    return find_newest_file_in_dir(directory, file_pattern='*.bin')


def main(argv):
    def show_options():
        print("To run experience, do:")
        print("> animate_hockey_game.py -d <experiments_root_dir> -e <experiment_name> -s <save_every_seconds> -r <record_in_minutes>")
        print("if <save_every_seconds> == -1 => 'record ALL steps of simulation' (warning: memory is cheap, not infinite)")
        #
        print("To display results of experience, do:")
        print("> animate_hockey_game.py -a <speedup> -i <input_file_name>")
    #
    DATA_EVERY_SECS = float("inf")
    RECORD_THIS_MANY_MINUTES = 0
    input_directory = ""
    speedup = 0
    experiment_name = None
    all_experiments_root_dir = None
    try:
      opts, args = getopt.getopt(argv,
                                 "hs:r:i:a:d:e:",
                                 ["save_every_seconds=",
                                  "record_in_minutes=",
                                  "input_directory=",
                                  "acceleration=",
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
        elif opt in ("-s", "--save_every_seconds"):
            DATA_EVERY_SECS = float(arg)
        elif opt in ("-r", "--record_in_minutes"):
            RECORD_THIS_MANY_MINUTES = int(arg)
        elif opt in ("-i", "--input_directory"):
            input_directory = str(arg)
        elif opt in ("-a", "--acceleration"):
            speedup = float(arg)
        elif opt in ("-d", "--experiments_root_dir="):
            all_experiments_root_dir = str(arg)
        elif opt in ("-e", "--experiment_name="):
            experiment_name = str(arg)
        else:
            print("Unrecognized option %s" % (opt))
    #
    if (DATA_EVERY_SECS != float("inf") and (speedup != 0)) or (DATA_EVERY_SECS == float("inf") and (speedup == 0)):
        show_options()
        raise RuntimeError("Either you generate data (by specifying -s and its companions) or you display data (by setting -d). You can't do both") # TODO: revise this message
    if (all_experiments_root_dir is None) or (experiment_name is None):
        show_options()
        raise RuntimeError("Both the root of the experiments and the experiment name has to be specified.")
    folder_manager = FolderManager(experiments_root_dir=all_experiments_root_dir, experiment_name=experiment_name)

    mode_simulation = DATA_EVERY_SECS != float("inf") # otherwise in mode visualization
    mode_visualization = not mode_simulation
    if mode_simulation:
        if DATA_EVERY_SECS == -1:
            DATA_EVERY_SECS = TIME_PER_FRAME
            print("Setting recording period to %.2f seconds" % (DATA_EVERY_SECS))
        elif DATA_EVERY_SECS <= 0:
            show_options()
            raise RuntimeError("[save every seconds] parameter must be > 0 (currently %.2f)" % (DATA_EVERY_SECS))
        if RECORD_THIS_MANY_MINUTES <= 0:
            show_options()
            raise RuntimeError("[record this many minutes] parameter must be > 0 (currently %.2f)" % (RECORD_THIS_MANY_MINUTES))
    if mode_visualization:
        if input_directory == "":
            raise RuntimeError("[mode = visualization] input directory must be specified")
        if speedup <= 0:
            raise RuntimeError("[mode = visualization] input directory must be specified")

    # field
    hockey_rink = HockeyHalfRink(
        width=HockeyHalfRink.WIDTH_HALF_ICE,
        height=HockeyHalfRink.HEIGHT_ICE,
        how_many_offense=1,
        how_many_defense=0,
        one_step_in_seconds=TIME_PER_FRAME,
        collect_data_every_secs=DATA_EVERY_SECS,
        record_this_many_minutes=RECORD_THIS_MANY_MINUTES)
    if mode_simulation:
        folder_manager.makedirs()
        # let's choose the name of the files were the data will be saved:
        # model
        print("************************** Choosing file name where to save model...")
        num_model_file = 1
        full_model_file_name = folder_manager.model_file_name(run_number=num_model_file, full=True)
        print("Trying '%s'..." % (full_model_file_name))
        # max_tick = 0
        max_step = 0
        max_goals = 0
        max_shots = 0
        max_timestamp = 0
        while os.path.exists(full_model_file_name):
            # update max's
            model_df = pd.read_csv(full_model_file_name)
            print(list(model_df.columns.values))
            # max_tick = max(max_tick, model_df["Unnamed: 0"].max())
            max_step = max(max_step, model_df["steps"].max())
            max_goals = max(max_goals, model_df["goals"].max())
            max_shots = max(max_shots, model_df["shots"].max())
            max_timestamp = max(max_timestamp, model_df["timestamp"].max())
            print("Updating max_steps to %d, max_goals to %d, max_shots to %d, max_timestamp to %.2f" % (max_step, max_goals, max_shots, max_timestamp))
            # new file to search
            num_model_file += 1
            full_model_file_name = folder_manager.model_file_name(run_number=num_model_file, full=True)
            print("Trying '%s'..." % (full_model_file_name))
        print("[Model file] Chosen '%s'" % (full_model_file_name))
        # agents
        print("************************** Choosing file name where to save agents...")
        num_agents_file = 1
        full_agents_file_name = folder_manager.agents_file_name(run_number=num_agents_file, full=True)
        print("Trying '%s'..." % (full_agents_file_name))
        while os.path.exists(full_agents_file_name):
            num_agents_file += 1
            full_agents_file_name = folder_manager.agents_file_name(run_number=num_agents_file, full=True)
            print("Trying '%s'..." % (full_agents_file_name))
        print("[Agents file] Chosen '%s'\n" % (full_agents_file_name))
        print("Will record %d minutes of simulated action, snapshots every %.2f seconds; reporting will be done in these dirs:\n%s"
              % (RECORD_THIS_MANY_MINUTES, DATA_EVERY_SECS, folder_manager.directories2str()))
        mesa_simulator = MesaModelSimulator(mesa_model=hockey_rink)
        hockey_problem = GrabThePuckProblem(hockey_world=hockey_rink)

        # where am I going to save to?
        brain_dir = folder_manager.brain_dir
        brain_name_opt = newest_brain_in_dir(brain_dir)

        # xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem, load_from_file_name="my_model_1.bin", save_to_file_name=None)
        # xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem, load_from_file_name="my_model_1.bin",
        #                                   save_to_file_name="my_model_1.bin")
        xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem, folder_manager=folder_manager)
        # xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem, load_from_file_name="my_model_1_2.bin", save_to_file_name="my_model_1_2.bin")
        # mesa_simulator.run()

        xcs_simulator.run_until_done() # run()
        #
        model_df = hockey_rink.datacollector.get_model_vars_dataframe()
        model_df["goals"] += max_goals
        model_df["shots"] += max_shots
        model_df["steps"] += max_step
        model_df["timestamp"] += max_timestamp

        agents_df = hockey_rink.datacollector.get_agent_vars_dataframe()
        print(list(agents_df.columns.values))
        agents_df["timestamp"] += max_timestamp

        model_df.to_csv(full_model_file_name)
        agents_df.to_csv(full_agents_file_name)

        # timestamp_reached = 0
        # while timestamp_reached < RECORD_THIS_MANY_MINUTES * 60:
        #     print("**************** RESTART **********************; I am on timestamp %d, going to %d" % (timestamp_reached, RECORD_THIS_MANY_MINUTES * 60))
        #     hockey_problem.reset()
        #     xcs_simulator.run()
        #     #
        #     model_df = hockey_rink.datacollector.get_model_vars_dataframe()
        #     timestamp_reached += model_df["timestamp"].max()
        #     model_df["goals"] += max_goals
        #     model_df["shots"] += max_shots
        #     model_df["steps"] += max_step
        #     model_df["timestamp"] += max_timestamp
        #
        #     agents_df = hockey_rink.datacollector.get_agent_vars_dataframe()
        #     print(list(agents_df.columns.values))
        #     agents_df["timestamp"] += max_timestamp
        #
        #     model_df.to_csv(full_model_file_name)
        #     agents_df.to_csv(full_agents_file_name)
        #
        #     # now update the 'max's
        #
        #     max_step = model_df["steps"].max()
        #     max_goals = model_df["goals"].max()
        #     max_shots = model_df["shots"].max()
        #     max_timestamp = model_df["timestamp"].max()
        #     print("Episode finished => I am on timestamp %d, going to %d" % (timestamp_reached, RECORD_THIS_MANY_MINUTES * 60))
    else:
        if not os.path.exists(input_directory):
            raise RuntimeError("Directory [%s] does not exist" % (input_directory))
        # all model files, concatenated
        model_df = read_and_merge_dataframes(input_directory, prefix_fname="model", verbose=True)
        num_steps = model_df["steps"].max()
        num_goals = model_df["goals"].max()
        print("[Recording length: %d minutes] %d steps of simulation, %d goals" % (RECORD_THIS_MANY_MINUTES, num_steps, num_goals))
        DATA_EVERY_SECS = round(model_df.iloc[2]["timestamp"] - model_df.iloc[1]["timestamp"], 5)
        # all agent files, concatenated
        agents_df = read_and_merge_dataframes(input_directory, prefix_fname="agents", verbose=True)
        print("Will visualize snapshots from [%s] at a speedup of %.2f"
              % (input_directory, speedup))

        # all renderings
        hockey_rink_renderable = HalfRinklPygameRenderable(hockey_rink)
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
                    hockey_rink.defense[defenses_seen].pos = the_pos
                    hockey_rink.defense[defenses_seen].angle_looking_at = speed_angle
                    hockey_rink.defense[defenses_seen].current_speed = speed_amplitude
                    hockey_rink.defense[defenses_seen].speed = hockey_rink.defense[defenses_seen].speed_on_xy()
                    defenses_seen += 1
                elif agent_id.startswith("forward"):
                    try:
                        hockey_rink.attack[attackers_seen].pos = the_pos
                    except Exception as e:
                        print("Exception of timestamp %d: %s" % (curr_timestamp, e))
                        print("attackers_seen = %d, len(hockey_rink.attack) = %d" % (attackers_seen, len(hockey_rink.attack)))
                    hockey_rink.attack[attackers_seen].angle_looking_at = speed_angle
                    hockey_rink.attack[attackers_seen].current_speed = speed_amplitude
                    hockey_rink.attack[attackers_seen].speed = hockey_rink.attack[attackers_seen].speed_on_xy()
                    attackers_seen += 1
                elif agent_id.startswith("puck"):
                    hockey_rink.puck.pos = the_pos
                else:
                    assert False
            # seconds_in_simulation = DATA_EVERY_SECS * i
            seconds_in_simulation = curr_timestamp
            minutes_in_simulation = seconds_in_simulation // 60
            if minutes_in_simulation > old_minutes_in_simulation:
                print("[%s] Minute %d of simulation" % (time.ctime(), minutes_in_simulation))
                old_minutes_in_simulation = minutes_in_simulation
            tick_time = clock.tick(FPS)
            times_between_frames.append(tick_time)
            surface.fill(THECOLORS['black']) # this is basically a CLEAR. TODO: can we do something better????
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame_render(hockey_rink_renderable.representation(), surface)
            pygame.display.update()

if __name__ == "__main__":
    main(sys.argv[1:])
