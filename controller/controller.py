from pathlib import Path
import os
import multiprocessing as mp

from interface.modules.arguments_types import *
from interface.modules.stacked_windows import StackedWindows

from model.arguments_types import *
from model.settings_data import SettingsData
from model.participant_data import ParticipantData
from model.quattrocento import QuattrocentoSettings, QuattrocentoClient
from model.sensoglove import AppSensoGloveClient, SensoGloveRawDataReader
from model.exercises_data import ExercisesData
from model.markup_data import MarkupDataReader
from model.data_merger import DataMerger

from .data_dictionaries import DataConverter
from .experiment_controller import ExperimentController


class Controller:

    def __init__(
            self,
            settings_dir: Path,
            patient_info_options: PatientInfoOptionsType,
            exercises_file_dir: Path,
            exercises_images_dir: Path
            ):

        self.data_converter = DataConverter()

        self.settings = SettingsData(settings_dir)

        self.save_dir = Path(self.settings['save_directory'])
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        self.quattrocent_ready_flag = mp.Event()
        self.sensoglove_ready_flag = mp.Event()
        self.start_flag = mp.Event()
        self.abort_flag = mp.Event()

        self.exercises_data = ExercisesData(exercises_file_dir, exercises_images_dir)
        
        main_windows_arguments: MainWindowArgumentsType = {
                'new_record_button_function': self.__main_window__new_record_button_function,
                'settings_button_function': self.__main_window__settings_button_function
            }
        
        settings_window_arguments: SettingsWindowArgumentsType = {
                'back_button_function': self.__settings_window__back_button_function,
                'save_button_function': self.__settings_window__save_button_function,
                'myograph_settings': self.settings['myograph_settings']['options']
            }
        
        patient_window_arguments: PatientWindowArgumentsType = {
                'back_button_function': self.__patient_window__back_button_function,
                'next_button_function': self.__patient_window__next_button_function,
                'patient_info_options': patient_info_options
            }

        connection_window_arguments: ConnectionWindowArgumentsType = {
                'connect_button_function': self.__connection_window__connect_button_function,
                'back_button_function': self.__connection_window__back_button_function,
                'start_record_button_function': self.__connection_window__start_record_button_function
            }

        experiment_window_arguments: ExperimentWindowArgumentsType = {
                'bar_info': {'min_value': 0, 'max_value': (len(self.exercises_data) - 1) * self.settings['experiment_settings']['repeats_number']}
            }

        finish_window_arguments: FinishWindowArgumentsType = {
                'main_menu_button_function': self.__finish_window__main_menu_button_function
            }

        stacked_windows_arguments: StackedWindowsArgumentsType = {
            'main_window_arguments': main_windows_arguments,
            'settings_window_arguments': settings_window_arguments,
            'patient_window_arguments': patient_window_arguments,
            'connection_window_arguments': connection_window_arguments,
            'experiment_window_arguments': experiment_window_arguments,
            'finish_window_arguments': finish_window_arguments
        }

        self.__stacked_windows = StackedWindows(stacked_windows_arguments)

    
    @property
    def stacked_windows(self):
        return self.__stacked_windows
    

    def __main_window__new_record_button_function(self):
        self.__stacked_windows.display_patient_info()


    def __main_window__settings_button_function(self):
        self.__stacked_windows.display_settings()


    def __settings_window__back_button_function(self):
        self.__stacked_windows.display_main_menu()


    def __settings_window__save_button_function(self):
        # TODO: finish function
        self.__stacked_windows.display_main_menu()


    def __patient_window__back_button_function(self):
        self.__stacked_windows.display_main_menu()
    

    def __patient_window__next_button_function(self):
        if self.__stacked_windows.patient_window.validate_text_fields():
            code, age, gender, hand = self.__stacked_windows.patient_window.get_patient_info()
            self.participant_data = ParticipantData(
                int(code),
                int(age),
                self.data_converter.convert_gender(gender),
                self.data_converter.convert_hand(hand)
                )
            self.participant_data.save_participant_info(self.save_dir)
            self.__make_raw_data_folder(code)
            self.save_file_dir = self.save_dir / (code + '.hdf5')
            self.__stacked_windows.display_connection()

            self.experiment_controller = ExperimentController(
                experiment_window=self.stacked_windows.experiment_window,
                save_dir=self.raw_files_dir,
                exercises=self.exercises_data,
                repeats_number=self.settings['experiment_settings']['repeats_number'],
                rest_time_in_s=self.settings['experiment_settings']['rest_time_in_s'],
                exercise_time_in_s=self.settings['experiment_settings']['exercise_time_in_s']
            )
    

    def __make_raw_data_folder(self, code: str):
        self.raw_files_dir = self.save_dir / 'raw' / code
        if not os.path.exists(self.raw_files_dir):
            os.makedirs(self.raw_files_dir)
    

    def __connect_to_quattrocento(self):
        quattrocento_settings = QuattrocentoSettings(self.settings['myograph_settings']['options'])
        self.quattrocento_client = QuattrocentoClient(
            ip_port=(self.settings['myograph_settings']['ip'], self.settings['myograph_settings']['port']),
            settings=quattrocento_settings,
            ready_flag=self.quattrocent_ready_flag,
            start_flag=self.start_flag,
            abort_flag=self.abort_flag,
            data_save_dir=self.save_file_dir
        )
        is_connected = self.quattrocento_client.make_connect()
        if is_connected:
            self.quattrocento_client.start()

            self.__stacked_windows.connection_window.change_myogragh_status('подключено', True)
        
        else:
            self.__stacked_windows.connection_window.change_myogragh_status('нет подключения', False)
    

    def __connect_to_sensoglove(self):
        self.sensoglove_client = AppSensoGloveClient(
            save_dir=self.raw_files_dir,
            start_flag=self.start_flag,
            ready_flag=self.sensoglove_ready_flag,
            abort_flag=self.abort_flag,
            ip_address=self.settings['glove_settings']['ip'],
            port=self.settings['glove_settings']['port']
        )
        is_connected = self.sensoglove_client.make_connect()
        if is_connected:
            self.sensoglove_client.start()

            self.__stacked_windows.connection_window.change_glove_status('подключено', True)
        
        else:
            self.__stacked_windows.connection_window.change_glove_status('нет подключения', False)

    def __start_record(self):
        self.abort_flag.clear()
        self.start_flag.set()
    

    def __stop_record(self):
        self.start_flag.clear()
        self.abort_flag.set()
        try:
            self.quattrocento_client.stop_listening()
            self.sensoglove_client.close_connection()
        except:
            pass


    def __connection_window__connect_button_function(self):
        self.__connect_to_quattrocento()
        self.__connect_to_sensoglove()


    def __connection_window__back_button_function(self):
        self.stacked_windows.display_patient_info()


    def __connection_window__start_record_button_function(self):
        if self.quattrocent_ready_flag.is_set() and self.sensoglove_ready_flag.is_set():
            self.__start_record()
            self.stacked_windows.display_experiment()
            self.experiment_controller.run()
            self.__stop_record()

            self.__merge_data()

            self.stacked_windows.display_finish()

    
    def __merge_data(self):
        markup_data = MarkupDataReader(self.raw_files_dir).load_data()
        sensoglove_data = SensoGloveRawDataReader(self.raw_files_dir).get_valuable_data()
        data_merger = DataMerger(self.save_file_dir)
        data_merger.merge_data(
            sensoglove_data=sensoglove_data,
            markup_data=markup_data
        )

    
    def __finish_window__main_menu_button_function(self):
        self.stacked_windows.display_main_menu()

    
    def close_all_connections(self):
        self.__stop_record()