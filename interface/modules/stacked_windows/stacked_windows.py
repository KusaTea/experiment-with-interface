from PySide6.QtWidgets import QStackedWidget

from ..windows import *
from ..arguments_types import *


class StackedWindows(QStackedWidget):

    def __init__(
            self,
            windows_arguments: StackedWindowsArgumentsType
            ):
        super().__init__()

        self.insert_all_windows(**windows_arguments)

        self.setCurrentIndex(0)
    

    def insert_all_windows(
            self,
            main_window_arguments: MainWindowArgumentsType,
            settings_window_arguments: SettingsWindowArgumentsType,
            patient_window_arguments: PatientWindowArgumentsType,
            connection_window_arguments: ConnectionWindowArgumentsType,
            experiment_window_arguments: ExperimentWindowArgumentsType,
            finish_window_arguments: FinishWindowArgumentsType
            ):
        self.main_window = MainWindow(**main_window_arguments)
        self.insertWidget(0, self.main_window)
        
        self.settings_window = SettingsWindow(**settings_window_arguments)
        self.insertWidget(1, self.settings_window)
        
        self.patient_window = PatientInfoWindow(**patient_window_arguments)
        self.insertWidget(2, self.patient_window)
        
        self.connection_window = ConnectionWindow(**connection_window_arguments)
        self.insertWidget(3, self.connection_window)
        
        self.experiment_window = ExperimentWindow(**experiment_window_arguments)
        self.insertWidget(4, self.experiment_window)
        
        self.finish_window = FinishWindow(**finish_window_arguments)
        self.insertWidget(5, self.finish_window)


    def display_main_menu(self):
        self.setCurrentIndex(0)

    def display_settings(self):
        self.setCurrentIndex(1)

    def display_patient_info(self):
        self.setCurrentIndex(2)

    def display_connection(self):
        self.setCurrentIndex(3)
    
    def display_experiment(self):
        self.setCurrentIndex(4)
    
    def display_finish(self):
        self.setCurrentIndex(5)
