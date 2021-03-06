import os
import glob
import re
from typing import Optional, Tuple, Callable
from util.base import find_newest_file_in_dir

class FolderManager(object):

    def __init__(self, experiments_root_dir: str, experiment_name: str):
        self.experiments_root_dir = experiments_root_dir
        self.experiment_name = experiment_name
        self.experiment_dir = os.path.join(self.experiments_root_dir, self.experiment_name)
        self.templates_prefix = "%s" % (self.experiment_name)
        self.brain_dir = os.path.join(self.experiment_dir, "brain")
        self.brain_evals_dir = os.path.join(self.brain_dir, "evals")
        self.model_dir = os.path.join(self.experiment_dir, "model")
        self.agents_dir = os.path.join(self.experiment_dir, "agents")

    def directories2str(self) -> str:
        return "experiment_dir = '%s'\n" % (self.experiment_dir) + \
               "brain_dir = '%s'\n" % (self.brain_dir) + \
               "brain_evals_dir = '%s'\n" % (self.brain_evals_dir) + \
               "model_dir = '%s'\n" % (self.model_dir) + \
               "agents_dir = '%s'\n" % (self.agents_dir)

    def makedirs(self):
        os.makedirs(self.experiment_dir, exist_ok=True)
        os.makedirs(self.brain_dir, exist_ok=True)
        os.makedirs(self.brain_evals_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.agents_dir, exist_ok=True)

    def __name_composer__(self, root_dir: str, str_id: str, idx_descr: str, idx: int, full: bool, ext: str) -> str:
        f_name = "%s_%s_%s_%d.%s" % (self.templates_prefix, str_id, idx_descr, idx, ext)
        return os.path.join(root_dir, f_name) if full else f_name

    def brain_file_name(self, episode: int, full: bool) -> str:
        return self.__name_composer__(root_dir=self.brain_dir, str_id="brain", idx_descr="episode", idx=episode, full=full, ext="bin")

    def brain_eval_file_name(self, episode: int, full: bool) -> str:
        return self.__name_composer__(root_dir=self.brain_evals_dir, str_id="eval", idx_descr="episode", idx=episode, full=full, ext="csv")

    def model_file_name(self, run_number: int, full: bool) -> str:
        return self.__name_composer__(root_dir=self.model_dir, str_id="model", idx_descr="run", idx=run_number, full=full, ext="pd")

    def agents_file_name(self, run_number: int, full: bool) -> str:
        return self.__name_composer__(root_dir=self.agents_dir, str_id="agents", idx_descr="run", idx=run_number, full=full, ext="pd")

    def newest_brain_file(self) -> Optional[str]:
        """Gets newest brain in a folder - None is there is nothing there or the directory doesn't exist."""
        return find_newest_file_in_dir(self.brain_dir, file_pattern='*.bin')

    def chose_brain_file_name(self) -> Tuple[int, str]:
        newest_brain = self.newest_brain_file()
        if newest_brain is None:
            new_brain_idx = 1
        else:
            numbers = re.findall(r'(\d+).bin', newest_brain)
            assert len(numbers) == 1, "newest_brain = %s, but I find several numbers (%s)" % (newest_brain, numbers)
            new_brain_idx = int(numbers[0]) + 1
        return new_brain_idx, self.brain_file_name(episode=new_brain_idx, full=True)

    def newest_model_file(self) -> Optional[str]:
        """Gets newest model's file in a folder - None is there is nothing there or the directory doesn't exist."""
        return find_newest_file_in_dir(self.model_dir, file_pattern='*.pd')

    def suggest_model_file_name(self) -> Tuple[int, str]:
        newest_model = self.newest_model_file()
        if newest_model is None:
            new_model_idx = 1
        else:
            numbers = re.findall(r'(\d+).pd', newest_model)
            assert len(numbers) == 1, "newest_model = %s, but I find several numbers (%s)" % (newest_model, numbers)
            new_model_idx = int(numbers[0]) + 1
        return new_model_idx, self.model_file_name(run_number=new_model_idx, full=True)

    def newest_agents_file(self) -> Optional[str]:
        """Gets newest agents' file in a folder - None is there is nothing there or the directory doesn't exist."""
        return find_newest_file_in_dir(self.model_dir, file_pattern='*.pd')

    def suggest_agents_file_name(self) -> Tuple[int, str]:
        newest = self.newest_agents_file()
        if newest is None:
            new_idx = 1
        else:
            numbers = re.findall(r'(\d+).pd', newest)
            assert len(numbers) == 1, "newest = %s, but I find several numbers (%s)" % (newest, numbers)
            new_idx = int(numbers[0]) + 1
        return new_idx, self.agents_file_name(run_number=new_idx, full=True)


