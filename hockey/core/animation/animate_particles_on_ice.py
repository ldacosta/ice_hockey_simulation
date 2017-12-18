import getopt
import os
import sys

import pandas as pd
from typing import Optional

from util.base import find_newest_file_in_dir
from hockey.behaviour.core.hockey_scenario import LearnToPlayHockeyProblem
from hockey.core.folder_manager import FolderManager
from hockey.core.model import TIME_PER_FRAME
from hockey.core.simulator import ScenarioSimulator
from hockey.core.ice_surface.ice_rink import SkatingIce


def read_and_merge_dataframes(input_directory, prefix_fname: str, verbose: bool = False) -> pd.DataFrame:
    all_fnames = [os.path.join(input_directory, fname)
                        for fname in os.listdir(input_directory) if fname.startswith(prefix_fname) and fname.endswith(".pd")]
    if verbose:
        print("From '%s' I read %s" % (input_directory, all_fnames))
    return pd.concat(list(map(pd.read_csv, all_fnames)), ignore_index=True)


def newest_brain_in_dir(directory: str) -> Optional[str]:
    """Gets newest brain in a folder - None is there is nothing there or the directory doesn't exist."""
    return find_newest_file_in_dir(directory, file_pattern='*.bin')

def show_options():
    print("To run experience, do:")
    print("> animate_particles_on_ice.py -d <experiments_root_dir> -e <experiment_name> -s <save_every_seconds> -r <record_in_minutes>")
    print("if <save_every_seconds> == -1 => 'record ALL steps of simulation' (warning: memory is cheap, not infinite)")

def animate(argv, ice_environment: SkatingIce, hockey_problem: LearnToPlayHockeyProblem):
    DATA_EVERY_SECS = float("inf")
    RECORD_THIS_MANY_MINUTES = 0
    experiment_name = None
    all_experiments_root_dir = None
    try:
      opts, args = getopt.getopt(argv,
                                 "hs:r:d:e:",
                                 ["save_every_seconds=",
                                  "record_in_minutes=",
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

    if DATA_EVERY_SECS == -1:
        DATA_EVERY_SECS = TIME_PER_FRAME
        print("Setting recording period to %.2f seconds" % (DATA_EVERY_SECS))
    elif DATA_EVERY_SECS <= 0:
        show_options()
        raise RuntimeError("[save every seconds] parameter must be > 0 (currently %.2f)" % (DATA_EVERY_SECS))
    if RECORD_THIS_MANY_MINUTES <= 0:
        show_options()
        raise RuntimeError("[record this many minutes] parameter must be > 0 (currently %.2f)" % (RECORD_THIS_MANY_MINUTES))

    ice_environment.setup_run(
        one_step_in_seconds=TIME_PER_FRAME,
        collect_data_every_secs=DATA_EVERY_SECS,
        record_this_many_minutes=RECORD_THIS_MANY_MINUTES)
    folder_manager.makedirs()
    print("Will record %d minutes of simulated action, snapshots every %.2f seconds; reporting will be done in these dirs:\n%s"
          % (RECORD_THIS_MANY_MINUTES, DATA_EVERY_SECS, folder_manager.directories2str()))
    # mesa_simulator = MesaModelSimulator(mesa_model=ice_environment)
    # hockey_problem = GrabThePuckProblem(hockey_world=ice_environment)
    hockey_problem.reset()

    # where am I going to save to?
    # brain_dir = folder_manager.brain_dir
    # brain_name_opt = newest_brain_in_dir(brain_dir)

    # xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem, load_from_file_name="my_model_1.bin", save_to_file_name=None)
    # xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem, load_from_file_name="my_model_1.bin",
    #                                   save_to_file_name="my_model_1.bin")
    xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem, folder_manager=folder_manager)
    # xcs_simulator = ScenarioSimulator(xcs_scenario=hockey_problem, load_from_file_name="my_model_1_2.bin", save_to_file_name="my_model_1_2.bin")
    # mesa_simulator.run()

    xcs_simulator.run_until_done() # run()
    #
    ice_environment.save_activity(folder_manager)
