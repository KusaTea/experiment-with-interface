from pathlib import Path
import os
from typing import Literal, Tuple, Callable

from PySide6.QtCore import QObject, Signal

from data.repositories import ParticipantData
from controller.modules import DirsStore, DataConverter


class ParticipantInfoWindowController(QObject):

    finished = Signal()
    back_button_pushed = Signal()
    next_button_pushed = Signal()

    def __init__(
            self,
            window,
            data_converter: DataConverter,
            dirs_store: DirsStore,
            stop_signal: Signal
            ):

        super().__init__()

        self.__data_converter = data_converter
        self.__dirs_store = dirs_store

        self.__participant_info_window = window
        self.__participant_info_window.add_callback_for_back_button(self.__back_callback)
        self.__participant_info_window.add_callback_for_next_button(self.__next_callback)

        stop_signal.connect(self.__finish)
    

    def __back_callback(self):
        self.__participant_info_window.reset()
        self.back_button_pushed.emit()


    def __next_callback(self):
        try:
            code, age, gender, hand = self.__participant_info_window.get_patient_info()
            self.__participant_data = ParticipantData(
                int(code),
                int(age),
                self.__data_converter.convert_gender(gender),
                self.__data_converter.convert_hand(hand)
                )
            self.__participant_data.save_participant_info(self.__dirs_store.data_main_dir)
            self.__make_raw_data_folder(code)
            self.__dirs_store.ready_data_dir(self.__dirs_store.data_main_dir / (code + '.hdf5'))
            self.__participant_info_window.reset()

            self.next_button_pushed.emit()
        
        except ValueError:
            pass

        except FileExistsError:
            del self.participant_data
            pass
    

    def __make_raw_data_folder(self, code: str):
        self.__dirs_store.raw_data_dir(self.__dirs_store.data_main_dir / 'raw' / code)
        if not os.path.exists(self.__raw_files_dir):
            os.makedirs(self.__raw_files_dir)

    
    def __finish(self):
        self.finished.emit()