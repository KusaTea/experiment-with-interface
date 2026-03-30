from pathlib import Path
import os
from typing import Literal, Tuple, Callable

from interface.modules.stacked_windows import StackedWindows
from model.participant_data import ParticipantData
from ..data_dictionaries import DataConverter


class ParticipantInfoWindowController:

    def __init__(
            self,
            stacked_windows: StackedWindows,
            data_converter: DataConverter,
            save_dir: Path,
            additional_callback_for_next_button: Callable = lambda: None
            ):
        self.__stacked_windows = stacked_windows
        self.__data_converter = data_converter
        self.__save_dir = save_dir
        self.__raw_files_dir = None

        self.__additional_callback_for_next_button: Callable = additional_callback_for_next_button

        self.__participant_info_window = self.__stacked_windows.patient_window
        self.__participant_info_window.add_callback_for_back_button(self.__back_callback)
        self.__participant_info_window.add_callback_for_next_button(self.__next_callback)
    

    def __back_callback(self):
        self.__stacked_windows.display_main_menu()
        self.__participant_info_window.reset()


    def __next_callback(self):
        try:
            code, age, gender, hand = self.__participant_info_window.get_patient_info()
            self.participant_data = ParticipantData(
                int(code),
                int(age),
                self.__data_converter.convert_gender(gender),
                self.__data_converter.convert_hand(hand)
                )
            self.participant_data.save_participant_info(self.__save_dir)
            self.__make_raw_data_folder(code)
            self.__save_file_dir = self.__save_dir / (code + '.hdf5')
            self.__stacked_windows.display_connection()
            self.__participant_info_window.reset()

            self.__additional_callback_for_next_button()
        
        except ValueError:
            pass

        except FileExistsError:
            del self.participant_data
            pass
    

    def __make_raw_data_folder(self, code: str):
        self.__raw_files_dir = self.__save_dir / 'raw' / code
        if not os.path.exists(self.__raw_files_dir):
            os.makedirs(self.__raw_files_dir)
    

    @property
    def raw_files_dir(self):
        return self.__raw_files_dir
    

    @property
    def save_file_dir(self):
        return self.__save_file_dir