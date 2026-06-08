from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from data.repositories import MarkupDataReader, SensogloveRawDataReader, EMGDataReader, DataMerger
from controller.modules import DirsStore


class DataMergerWorker(QObject):

    finished = Signal()
    saved_file = Signal(str)

    def __init__(self, dirs_store: DirsStore):
        super().__init__()

        self.__dirs_store = dirs_store


    def run(self):
        markup_data = MarkupDataReader(self.__dirs_store.raw_data_dir).load_data()
        sensoglove_data = SensogloveRawDataReader(self.__dirs_store.raw_data_dir).get_valuable_data()
        emg_data = EMGDataReader(self.__dirs_store.raw_data_dir).get_emg_data()
        data_merger = DataMerger(self.__dirs_store.ready_data_dir)
        data_merger.merge_data(
            emg_data=emg_data,
            sensoglove_data=sensoglove_data,
            markup_data=markup_data
        )

        self.saved_file.emit(str(self.__dirs_store.ready_data_dir.absolute()))
        self.finished.emit()


class FinishWindowController(QObject):

    finished = Signal()
    main_window_button_pushed = Signal()

    def __init__(
            self,
            window,
            dirs_store: DirsStore,
            start_merging_signal: Signal
    ):

        super().__init__()

        self.__finish_window = window
        self.__finish_window.add_callback_for_main_menu_button(self.__main_window_callback)

        self.__dirs_store = dirs_store

        self.__create_data_merger_thread()

        self.__finish_window.change_save_directory_label('в процессе...')
        self.__enable_button(False)

        start_merging_signal.connect(self.__start_merger_thread)
    

    def __enable_button(self, enable: bool = True):
        self.__finish_window.main_menu_button.setEnabled(enable)


    def __main_window_callback(self):
        self.main_window_button_pushed.emit()
        self.__finish_window.change_save_directory_label('в процессе...')
        self.__enable_button(False)
    

    def __create_data_merger_thread(self):
        self.__data_merger_worker = DataMergerWorker(self.__dirs_store)
        self.__thread = QThread()

        self.__data_merger_worker.moveToThread(self.__thread)

        self.__thread.started.connect(self.__data_merger_worker.run)

        self.__data_merger_worker.saved_file.connect(self.__finish_window.change_save_directory_label)

        self.__data_merger_worker.finished.connect(self.__enable_button)

        self.__data_merger_worker.finished.connect(self.__thread.quit)
        self.__data_merger_worker.finished.connect(self.__data_merger_worker.deleteLater)
        self.__thread.finished.connect(self.__thread.deleteLater)
    

    def __start_merger_thread(self):
        self.__thread.start()