import multiprocessing
from pathlib import Path
from time import sleep, time
from typing import Tuple, Callable

from PySide6.QtCore import QObject, QThread, Signal

from interface.modules.stacked_windows import StackedWindows
from model.exercises_data import ExercisesData, ExercisesIterator
from model.markup_data import MarkupDataCreater


class ExperimentWorker(QObject):

    finished = Signal()
    increase_progress = Signal(int)
    current_event = Signal(str)
    event_green_color = Signal()
    event_orange_color = Signal()
    current_exercise_name = Signal(str)
    current_exercise_image_dir = Signal(str)
    timer_value = Signal(str)

    def __init__(
            self,
            save_dir: Path | None,
            exercises_file_dir: Path,
            exercises_images_dir: Path,
            repeats_number: int,
            rest_time_in_s: int,
            exercise_time_in_s: int
            ):
        super().__init__()

        self.__save_dir = save_dir

        self.__exercises_data = ExercisesData(exercises_file_dir, exercises_images_dir)
        
        self.__rest_time_in_s = rest_time_in_s
        self.__exercise_time_in_s = exercise_time_in_s
        
        self.__exercises_iterator = ExercisesIterator(
            repeats_number=repeats_number,
            number_of_exercises=len(self.__exercises_data) - 2
            )
    

    @property
    def number_of_exercises(self) -> int:
        return len(self.__exercises_iterator)


    def __create_markup_data_creater(self):
        if not self.__save_dir:
            raise ValueError('save_dir is None')

        self.__markup_creater = MarkupDataCreater(self.__save_dir)


    def __start_calibration(self):
        start_ts = time()

        self.current_event.emit('ОТДЫХ')
        self.event_green_color.emit()
        self.current_exercise_name.emit(self.__exercises_data.get_exercise_name(-1))
        self.current_exercise_image_dir.emit(str(self.__exercises_data.get_exercise_image_dir(-1).absolute()))


        self.__markup_creater.save_data(str(start_ts), 0)

        while (calib_start_ts := time()) - start_ts < self.__rest_time_in_s:
            self.timer_value.emit(str(int(self.__rest_time_in_s - (calib_start_ts - start_ts))))
            sleep(0.1)

        self.current_event.emit('КАЛИБРОВКА')
        self.event_orange_color.emit()
        self.__markup_creater.save_data(str(calib_start_ts), -1)

        while (calib_end_ts := time()) - calib_start_ts < self.__exercise_time_in_s:
            self.timer_value.emit(str(int(self.__exercise_time_in_s - (calib_end_ts - calib_start_ts))))
            sleep(0.1)
        
        self.current_event.emit('ОТДЫХ')
        self.event_green_color.emit()
        self.__markup_creater.save_data(str(calib_end_ts), 0)


    def __experiment_step(self, exercise_idx):
        start_ts = time()

        self.current_event.emit('ОТДЫХ')
        self.event_green_color.emit()
        self.current_exercise_name.emit(self.__exercises_data.get_exercise_name(exercise_idx))
        self.current_exercise_image_dir.emit(str(self.__exercises_data.get_exercise_image_dir(exercise_idx).absolute()))

        self.__markup_creater.save_data(str(start_ts), 0)

        while (exercise_start_ts := time()) - start_ts < self.__rest_time_in_s:
            self.timer_value.emit(str(int(self.__rest_time_in_s - (exercise_start_ts - start_ts))))
            sleep(0.1)

        self.current_event.emit('УПРАЖНЕНИЕ')
        self.event_orange_color.emit()
        self.__markup_creater.save_data(str(exercise_start_ts), exercise_idx)

        while (exercise_end_ts := time()) - exercise_start_ts < self.__exercise_time_in_s:
            self.timer_value.emit(str(int(self.__exercise_time_in_s - (exercise_end_ts - exercise_start_ts))))
            sleep(0.1)
        
        self.current_event.emit('ОТДЫХ')
        self.event_green_color.emit()
        self.increase_progress.emit(1)
        self.__markup_creater.save_data(str(exercise_end_ts), exercise_idx)


    def __start_experiment(self):
        for exercise_idx in self.__exercises_iterator:
            self.__experiment_step(exercise_idx)
        self.__markup_creater.close_file()
    

    def run(self):
        self.__create_markup_data_creater()
        self.__start_calibration()
        self.__start_experiment()
        self.finished.emit()


class ExperimentWindowController:

    def __init__(
            self,
            stacked_windows: StackedWindows,
            exercises_file_dir: Path,
            exercises_images_dir: Path,
            experiment_settings: dict,
            background_image_dir: Path,
            additional_callback_after_record: Callable = lambda: None
            ):
        
        self.__stacked_windows = stacked_windows
        self.__experiment_window = stacked_windows.experiment_window
        
        self.__additional_callback_after_record: Callable = additional_callback_after_record

        self.__exercises_file_dir = exercises_file_dir
        self.__exercises_images_dir = exercises_images_dir
        self.update_experiment_settings(experiment_settings)

        self.__background_image_dir = str(background_image_dir.absolute()).replace('\\', '/')

    
    def update_experiment_settings(self, settings: dict):
        self.__rest_time_in_s = settings['rest_time_in_s']
        self.__exercise_time_in_s = settings['exercise_time_in_s']
        self.__repeats_number = settings['repeats_number']
        

    def __stop_experiment_thread(self):
        self.__stacked_windows.display_finish()
        self.__additional_callback_after_record()

    
    def create_experiment_thread(self, save_dir: Path):
        self.__experiment_worker = ExperimentWorker(
            save_dir,
            self.__exercises_file_dir,
            self.__exercises_images_dir,
            self.__repeats_number,
            self.__rest_time_in_s,
            self.__exercise_time_in_s
        )
        self.__thread = QThread()
        
        self.__experiment_window.change_bar_info(min_value=0, max_value=self.__experiment_worker.number_of_exercises)

        self.__experiment_worker.moveToThread(self.__thread)

        self.__thread.started.connect(self.__experiment_worker.run)

        self.__experiment_worker.increase_progress.connect(self.__experiment_window.change_progress)
        self.__experiment_worker.current_event.connect(self.__experiment_window.change_event_text)
        self.__experiment_worker.event_green_color.connect(self.__experiment_window.change_event_text_color_to_green)
        self.__experiment_worker.event_green_color.connect(lambda: self.__experiment_window.change_background_image(self.__background_image_dir))
        self.__experiment_worker.event_orange_color.connect(self.__experiment_window.change_event_text_color_to_orange)
        self.__experiment_worker.event_orange_color.connect(self.__experiment_window.remove_background_image)
        self.__experiment_worker.current_exercise_name.connect(self.__experiment_window.change_exercise_name)
        self.__experiment_worker.current_exercise_image_dir.connect(self.__experiment_window.change_exercise_image)
        self.__experiment_worker.timer_value.connect(self.__experiment_window.change_timer)
        
        self.__experiment_worker.finished.connect(self.__thread.quit)
        self.__experiment_worker.finished.connect(self.__experiment_worker.deleteLater)
        self.__experiment_worker.finished.connect(self.__stop_experiment_thread)
        self.__thread.finished.connect(self.__thread.deleteLater)
    

    def start_experiment_thread(self):
        self.__thread.start()