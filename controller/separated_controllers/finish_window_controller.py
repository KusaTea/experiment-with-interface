from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from interface.modules.stacked_windows import StackedWindows
from model.markup_data import MarkupDataReader
from model.data_merger import DataMerger
from model.sensoglove import SensogloveRawDataReader
from model.quattrocento import EMGDataReader


class DataMergerWorker(QObject):

    finished = Signal()
    saved_file = Signal(str)

    def __init__(self, raw_files_dir: Path, save_file_dir: Path):
        super().__init__()

        self.__raw_files_dir = raw_files_dir
        self.__save_file_dir = save_file_dir


    def run(self):
        markup_data = MarkupDataReader(self.__raw_files_dir).load_data()
        sensoglove_data = SensogloveRawDataReader(self.__raw_files_dir).get_valuable_data()
        emg_data = EMGDataReader(self.__raw_files_dir).get_emg_data()
        data_merger = DataMerger(self.__save_file_dir)
        data_merger.merge_data(
            emg_data=emg_data,
            sensoglove_data=sensoglove_data,
            markup_data=markup_data
        )

        self.saved_file.emit(str(self.__save_file_dir.absolute()))
        self.finished.emit()


class FinishWindowController:

    def __init__(
            self,
            stacked_windows: StackedWindows
    ):
        self.__stacked_windows = stacked_windows

        self.__finish_window = self.__stacked_windows.finish_window
        self.__finish_window.add_callback_for_main_menu_button(self.__main_window_callback)

        self.__finish_window.change_save_directory_label('в процессе...')
        self.__enable_button(False)
    

    def __enable_button(self, enable: bool = True):
        self.__finish_window.main_menu_button.setEnabled(enable)


    def __main_window_callback(self):
        self.__stacked_windows.display_main_menu()
        self.__finish_window.change_save_directory_label('в процессе...')
        self.__enable_button(False)
    

    def create_data_merger_thread(self, raw_files_dir: Path, save_file_dir: Path):
        self.__data_merger_worker = DataMergerWorker(raw_files_dir, save_file_dir)
        self.__thread = QThread()

        self.__data_merger_worker.moveToThread(self.__thread)

        self.__thread.started.connect(self.__data_merger_worker.run)

        self.__data_merger_worker.saved_file.connect(self.__finish_window.change_save_directory_label)

        self.__data_merger_worker.finished.connect(self.__enable_button)

        self.__data_merger_worker.finished.connect(self.__thread.quit)
        self.__data_merger_worker.finished.connect(self.__data_merger_worker.deleteLater)
        self.__thread.finished.connect(self.__thread.deleteLater)
    

    def start_finish_thread(self):
        self.__thread.start()