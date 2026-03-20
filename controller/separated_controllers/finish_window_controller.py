from pathlib import Path

from interface.modules.stacked_windows import StackedWindows
from model.markup_data import MarkupDataReader
from model.data_merger import DataMerger
from model.sensoglove import SensogloveRawDataReader


class FinishWindowController:

    def __init__(
            self,
            stacked_windows: StackedWindows
    ):
        self.__stacked_windows = stacked_windows

        self.__finish_window = self.__stacked_windows.finish_window
        self.__finish_window.add_callback_for_main_menu_button(self.__main_window_callback)
    

    def __main_window_callback(self):
        self.__stacked_windows.display_main_menu()
        self.__finish_window.change_save_directory_label('')

    
    def __merge_data(self, raw_files_dir: Path, save_file_dir: Path):
        markup_data = MarkupDataReader(raw_files_dir).load_data()
        sensoglove_data = SensogloveRawDataReader(raw_files_dir).get_valuable_data()
        data_merger = DataMerger(save_file_dir)
        data_merger.merge_data(
            sensoglove_data=sensoglove_data,
            markup_data=markup_data
        )


    def update_window_info(self, raw_files_dir: Path, save_file_dir: Path):
        self.__finish_window.change_save_directory_label('в процессе...')
        self.__merge_data(raw_files_dir, save_file_dir)
        self.__finish_window.change_save_directory_label(str(save_file_dir.absolute()))