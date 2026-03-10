import multiprocessing
from pathlib import Path

from time import sleep, time

from typing import Tuple

from interface.modules.windows import ExperimentWindow
from model.exercises_data import ExercisesData, ExercisesIterator
from model.markup_data import MarkupDataCreater


class ExperimentController:

    def __init__(
            self,
            experiment_window: ExperimentWindow,
            save_dir: Path,
            exercises: ExercisesData,
            repeats_number: int = 5,
            rest_time_in_s: int = 10,
            exercise_time_in_s: int = 5,
            ):
        
        self.window = experiment_window
        
        self.exercises = exercises
        self.exercises_iterator = ExercisesIterator(
            repeats_number=repeats_number,
            number_of_exercises=len(self.exercises)
            )
        
        self.markup_creater = MarkupDataCreater(save_dir)

        self.rest_time = rest_time_in_s
        self.exercises_time = exercise_time_in_s


    def start_calibration(self):
        start_ts = time()

        self.window.change_event('ОТДЫХ')
        self.window.change_exercise(
            self.exercises.get_exercise_name(-1),
            self.exercises.get_exercise_image_dir(-1)
        )

        self.markup_creater.save_data(str(start_ts), 0)

        while (calib_start_ts := time()) - start_ts < self.rest_time:
            self.window.change_timer(str(int(calib_start_ts - start_ts)))
            sleep(1)

        self.window.change_event('КАЛИБРОВКА')
        self.markup_creater.save_data(str(calib_start_ts), -1)

        while (calib_end_ts := time()) - calib_start_ts < self.exercises_time:
            self.window.change_timer(str(int(calib_end_ts - calib_start_ts)))
            sleep(1)
        
        self.window.change_event('ОТДЫХ')
        self.markup_creater.save_data(str(calib_end_ts), 0)


    def experiment_step(self, exercise_idx):
        start_ts = time()

        self.window.change_event('ОТДЫХ')
        self.window.change_exercise(
            self.exercises.get_exercise_name(exercise_idx),
            self.exercises.get_exercise_image_dir(exercise_idx)
        )

        self.markup_creater.save_data(str(start_ts), 0)

        while (exercise_start_ts := time()) - start_ts < self.rest_time:
            self.window.change_timer(str(int(exercise_start_ts - start_ts)))
            sleep(1)

        self.window.change_event('УПРАЖНЕНИЕ')
        self.markup_creater.save_data(str(exercise_start_ts), exercise_idx)

        while (exercise_end_ts := time()) - exercise_start_ts < self.exercises_time:
            self.window.change_timer(str(int(exercise_end_ts - exercise_start_ts)))
            sleep(1)
        
        self.window.change_event('ОТДЫХ')
        self.window.change_progress()
        self.markup_creater.save_data(str(exercise_end_ts), exercise_idx)


    def start_experiment(self):
        for exercise_idx in self.exercises_iterator:
            self.experiment_step(exercise_idx)
    
    
    def stop_experiment(self):
        del(self.markup_creater)
    

    def run(self):
        self.start_calibration()
        self.start_experiment()
        self.stop_experiment()