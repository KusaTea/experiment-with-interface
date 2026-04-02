from pathlib import Path
import os
import multiprocessing as mp

from interface.modules.arguments_types import *
from interface.modules.stacked_windows import StackedWindows

from model.arguments_types import *
from model.settings_data import SettingsData

from .data_dictionaries import DataConverter
from .separated_controllers import MainWindowController, SettingsWindowController, ParticipantInfoWindowController, ConnectionWindowController, ExperimentWindowController, FinishWindowController


class Controller:

    def __init__(
            self,
            settings_dir: Path,
            patient_info_options: PatientInfoOptionsType,
            exercises_file_dir: Path,
            exercises_images_dir: Path
            ):

        self.__data_converter = DataConverter()

        self.__settings = SettingsData(settings_dir)

        self.__save_dir = Path(self.__settings['save_directory'])
        if not os.path.exists(self.__save_dir):
            os.makedirs(self.__save_dir)
        
        patient_window_arguments: PatientWindowArgumentsType = {
                'patient_info_options': patient_info_options
            }

        experiment_window_arguments: ExperimentWindowArgumentsType = {
            'bar_info': {'min_value': 0, 'max_value': 1}
        }

        stacked_windows_arguments: StackedWindowsArgumentsType = {
            'patient_window_arguments': patient_window_arguments,
            'experiment_window_arguments': experiment_window_arguments
        }

        self.__stacked_windows = StackedWindows(stacked_windows_arguments)

        self.__main_window_controller = MainWindowController(self.__stacked_windows)
        
        self.__settings_window_controller = SettingsWindowController(
            self.__stacked_windows,
            settings=self.__settings,
            additional_callback_for_save_button=self.__update_settings
            )
        
        self.__participant_info_window_controller = ParticipantInfoWindowController(
            stacked_windows=self.__stacked_windows,
            data_converter=self.__data_converter,
            save_dir=self.__save_dir,
            additional_callback_for_next_button = self.__update_dirs_info
        )
        
        self.__connection_window_controller = ConnectionWindowController(
            stacked_windows=self.__stacked_windows,
            settings=self.__settings,
            raw_files_dir=self.__participant_info_window_controller.raw_files_dir,
            additional_callback_for_start_record=self.__callback_for_start_record
        )
        
        self.__experiment_window_controller = ExperimentWindowController(
            stacked_windows=self.__stacked_windows,
            exercises_file_dir=exercises_file_dir,
            exercises_images_dir=exercises_images_dir,
            experiment_settings=self.__settings['experiment_settings'],
            additional_callback_after_record=self.__callback_for_experiment_finish,
        )

        self.__finish_window_controller = FinishWindowController(self.__stacked_windows)


    @property
    def stacked_windows(self):
        return self.__stacked_windows
    

    def __update_dirs_info(self):
        self.__connection_window_controller.raw_files_dir = self.__participant_info_window_controller.raw_files_dir
    

    def __callback_for_start_record(self):
        self.__experiment_window_controller.create_experiment_thread(self.__participant_info_window_controller.raw_files_dir)
        self.__experiment_window_controller.start_experiment_thread()


    def __callback_for_experiment_finish(self):
        if not self.__participant_info_window_controller.raw_files_dir:
            raise ValueError('raw_files_dir is None')
        
        self.__connection_window_controller.stop_record()

        self.__finish_window_controller.create_data_merger_thread(
            self.__participant_info_window_controller.raw_files_dir,
            self.__participant_info_window_controller.save_file_dir
        )
        self.__finish_window_controller.start_finish_thread()
    

    def __update_settings(self, new_settings):
        self.__settings.update_settings(new_settings)

        self.__save_dir = Path(self.__settings['save_directory'])
        if not os.path.exists(self.__save_dir):
            os.makedirs(self.__save_dir)

        self.__participant_info_window_controller.update_save_dir(self.__save_dir)
        
        self.__connection_window_controller.update_settings(self.__settings)
        self.__experiment_window_controller.update_experiment_settings(self.__settings['experiment_settings'])