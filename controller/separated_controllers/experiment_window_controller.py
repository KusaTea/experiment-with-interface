import multiprocessing
from pathlib import Path

from time import sleep, time

from typing import Tuple

from interface.modules.stacked_windows import StackedWindows
from model.exercises_data import ExercisesData, ExercisesIterator
from model.markup_data import MarkupDataCreater


class ExperimentWindowController:

    def __init__(
            self,
            stacked_windows: StackedWindows,
            save_dir: Path,
            exercises_file_dir: Path,
            exercises_images_dir: Path,
            repeats_number: int = 5,
            rest_time_in_s: int = 10,
            exercise_time_in_s: int = 5,
            ):
        
        self.__stacked_windows = stacked_windows
        self.__experinet_window = stacked_windows.experiment_window
        
        self.__exercises_data = ExercisesData(exercises_file_dir, exercises_images_dir)
        self.__exercises_iterator = ExercisesIterator(
            repeats_number=repeats_number,
            number_of_exercises=len(self.__exercises_data)
            )
        
        self.__experinet_window.change_bar_info(min_value=0, max_value=len(self.__exercises_iterator))
        
        self.markup_creater = MarkupDataCreater(save_dir)

        self.rest_time = rest_time_in_s
        self.exercises_time = exercise_time_in_s


    def __start_calibration(self):
        start_ts = time()

        self.__experinet_window.change_event('ОТДЫХ')
        self.__experinet_window.change_exercise(
            self.__exercises_data.get_exercise_name(-1),
            self.__exercises_data.get_exercise_image_dir(-1)
        )

        self.markup_creater.save_data(str(start_ts), 0)

        while (calib_start_ts := time()) - start_ts < self.rest_time:
            self.__experinet_window.change_timer(str(int(calib_start_ts - start_ts)))
            sleep(1)

        self.__experinet_window.change_event('КАЛИБРОВКА')
        self.markup_creater.save_data(str(calib_start_ts), -1)

        while (calib_end_ts := time()) - calib_start_ts < self.exercises_time:
            self.__experinet_window.change_timer(str(int(calib_end_ts - calib_start_ts)))
            sleep(1)
        
        self.__experinet_window.change_event('ОТДЫХ')
        self.markup_creater.save_data(str(calib_end_ts), 0)


    def __experiment_step(self, exercise_idx):
        start_ts = time()

        self.__experinet_window.change_event('ОТДЫХ')
        self.__experinet_window.change_exercise(
            self.__exercises_data.get_exercise_name(exercise_idx),
            self.__exercises_data.get_exercise_image_dir(exercise_idx)
        )

        self.markup_creater.save_data(str(start_ts), 0)

        while (exercise_start_ts := time()) - start_ts < self.rest_time:
            self.__experinet_window.change_timer(str(int(exercise_start_ts - start_ts)))
            sleep(1)

        self.__experinet_window.change_event('УПРАЖНЕНИЕ')
        self.markup_creater.save_data(str(exercise_start_ts), exercise_idx)

        while (exercise_end_ts := time()) - exercise_start_ts < self.exercises_time:
            self.__experinet_window.change_timer(str(int(exercise_end_ts - exercise_start_ts)))
            sleep(1)
        
        self.__experinet_window.change_event('ОТДЫХ')
        self.__experinet_window.change_progress()
        self.markup_creater.save_data(str(exercise_end_ts), exercise_idx)


    def __start_experiment(self):
        for exercise_idx in self.__exercises_iterator:
            self.__experiment_step(exercise_idx)
    

    def __stop_experiment(self):
        self.__stacked_windows.display_finish()
    

    def run(self):
        self.__start_calibration()
        self.__start_experiment()
        self.__stop_experiment()