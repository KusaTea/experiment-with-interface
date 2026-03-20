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

        
        settings_window_arguments: SettingsWindowArgumentsType = {
                'myograph_settings': self.__settings['myograph_settings']['options']
            }
        
        patient_window_arguments: PatientWindowArgumentsType = {
                'patient_info_options': patient_info_options
            }

        experiment_window_arguments: ExperimentWindowArgumentsType = {
            'bar_info': {'min_value': 0, 'max_value': 1}
        }

        stacked_windows_arguments: StackedWindowsArgumentsType = {
            'settings_window_arguments': settings_window_arguments,
            'patient_window_arguments': patient_window_arguments,
            'experiment_window_arguments': experiment_window_arguments
        }

        self.__stacked_windows = StackedWindows(stacked_windows_arguments)


        # TODO: solve the problem with participant data and raw files dir update
        self.__main_window_controller = MainWindowController(self.__stacked_windows)
        self.__settings_window_controller = SettingsWindowController(self.__stacked_windows)
        self.__participant_info_window_controller = ParticipantInfoWindowController(
            stacked_windows=self.__stacked_windows,
            data_converter=self.__data_converter,
            save_dir=self.__save_dir
        )
        self.__connection_window_controller = ConnectionWindowController(
            stacked_windows=self.__stacked_windows,
            settings=self.__settings,
            raw_files_dir=self.__participant_info_window_controller.raw_files_dir
        )
        self.__experiment_window_controller = ExperimentWindowController(
            stacked_windows=self.__stacked_windows,
            save_dir=self.__participant_info_window_controller.raw_files_dir,
            exercises_file_dir=exercises_file_dir,
            exercises_images_dir=exercises_images_dir
        )

    
    @property
    def stacked_windows(self):
        return self.__stacked_windows