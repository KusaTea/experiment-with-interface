from pathlib import Path
import os

from PySide6.QtCore import Signal, QObject

from view.types import *
from view import StackedWindows

from data.types import *
from data.repositories import SettingsData

from controller.separated_controllers import MainWindowController, SettingsWindowController, ParticipantInfoWindowController, ConnectionWindowController, ExperimentWindowController, FinishWindowController
from controller.modules import DirsStore, DataConverter

from utils.dirs_data import settings_dir, exercises_dir, exercises_images_dir, background_images_dirs
from utils.view_data import participant_info_options, bar_info

class Controller(QObject):

    common_stop_signal = Signal()
    settings_updated_signal = Signal()
    start_experiment_signal = Signal()
    stop_experiment_signal = Signal()

    def __init__(self):

        super().__init__()

        self.__data_converter = DataConverter()

        self.__settings = SettingsData(settings_dir)

        data_main_dir = Path(self.__settings['save_directory'])
        if not os.path.exists(data_main_dir):
            os.makedirs(data_main_dir)

        self.__dirs_store = DirsStore(
            data_main_dir=data_main_dir,
            exercises_dir=exercises_dir,
            exercises_images_dir=exercises_images_dir,
            background_image_dir=background_images_dirs
        )
        
        patient_window_arguments: PatientWindowArgumentsType = {
                'patient_info_options': participant_info_options
            }

        experiment_window_arguments: ExperimentWindowArgumentsType = {
            'bar_info': bar_info
        }

        stacked_windows_arguments: StackedWindowsArgumentsType = {
            'patient_window_arguments': patient_window_arguments,
            'experiment_window_arguments': experiment_window_arguments
        }

        self.__stacked_windows = StackedWindows(stacked_windows_arguments)

        self.__main_window_controller = MainWindowController(
            window= self.__stacked_windows.main_window,
            stop_signal=self.common_stop_signal
            )
        self.__main_window_controller.new_record_button_pushed.connect(
            self.__stacked_windows.display_patient_info
        )
        self.__main_window_controller.settings_button_pushed.connect(
            self.__stacked_windows.display_settings
        )
        
        self.__settings_window_controller = SettingsWindowController(
            window=self.__stacked_windows.settings_window,
            settings=self.__settings,
            stop_signal=self.common_stop_signal
        )
        self.__settings_window_controller.back_button_pushed.connect(
            self.__stacked_windows.display_main_menu
        )
        self.__settings_window_controller.save_button_pushed.connect(
            self.__stacked_windows.display_main_menu,
            self.settings_updated_signal.emit()
        )

        self.__participant_info_window_controller = ParticipantInfoWindowController(
            window=self.__stacked_windows.patient_window,
            data_converter=self.__data_converter,
            dirs_store=self.__dirs_store,
            stop_signal=self.common_stop_signal
        )
        self.__participant_info_window_controller.back_button_pushed.connect(
            self.__stacked_windows.display_main_menu
        )
        self.__participant_info_window_controller.next_button_pushed.connect(
            self.__stacked_windows.display_connection
        )
        
        self.__connection_window_controller = ConnectionWindowController(
            window=self.__stacked_windows.connection_window,
            settings=self.__settings,
            dirs_store=self.__dirs_store,
            settings_updated=self.settings_updated_signal,
            stop_signal=self.stop_experiment_signal
        )
        self.__connection_window_controller.back_button_pushed.connect(
            self.__stacked_windows.display_patient_info
        )
        self.__connection_window_controller.start_record_button_pushed.connect(
            self.__start_experiment_callback
        )
        
        self.__experiment_window_controller = ExperimentWindowController(
            window=self.__stacked_windows.experiment_window,
            dirs_store=self.__dirs_store,
            settings=self.__settings,
            start_experiment_signal=self.start_experiment_signal,
            stop_signal=self.common_stop_signal
        )
        self.__experiment_window_controller.experiment_finished.connect(
            self.__stop_experiment_callback
        )

        self.__finish_window_controller = FinishWindowController(
            window=self.__stacked_windows.finish_window,
            dirs_store=self.__dirs_store,
            start_merging_signal=self.stop_experiment_signal
        )
        self.__finish_window_controller.main_window_button_pushed.connect(
            self.__stacked_windows.display_main_menu
        )


    @property
    def stacked_windows(self):
        return self.__stacked_windows


    def __start_experiment_callback(self):
        self.start_experiment_signal.emit()
        self.__stacked_windows.display_experiment()


    def __stop_experiment_callback(self):
        self.stop_experiment_signal.emit()
        self.__stacked_windows.display_finish()