from pathlib import Path
import multiprocessing as mlp
from typing import Callable
from time import sleep

from interface.modules.stacked_windows import StackedWindows
from model.settings_data import SettingsData
from model.sensoglove import SensogloveModule, SensogloveDataHandler
from model.quattrocento import QuattrocentoModule, QuattrocentoDataHandler, QuattrocentoSettings


class ConnectionWindowController:

    def __init__(
            self,
            stacked_windows: StackedWindows,
            settings: SettingsData,
            raw_files_dir: Path | None,
            additional_callback_for_start_record: Callable = lambda: None
            ):
        self.__stacked_windows = stacked_windows
        self.__additional_callback_for_start_record: Callable = additional_callback_for_start_record
        
        self.__raw_files_dir = raw_files_dir
        self.__raw_files_dir_changed = True

        self.__start_flag = mlp.Event()
        self.__abort_flag = mlp.Event()

        self.__sensoglove_module = SensogloveModule(
            ip_address=settings['glove_settings']['ip'],
            port=settings['glove_settings']['port']
        )

        self.__quattrocento_settings = QuattrocentoSettings(settings['myograph_settings']['options'])
        self.__quattrocento_module = QuattrocentoModule(
            ip_address=settings['myograph_settings']['ip'],
            port=settings['myograph_settings']['port'],
            buffer_size=self.__quattrocento_settings.buffer_size
        )
        

        self.__connection_window = self.__stacked_windows.connection_window
        self.__connection_window.add_callback_for_connect_button(self.__connect_callback)
        self.__connection_window.add_callback_for_back_button(self.__back_callback)
        self.__connection_window.add_callback_for_start_record_button(self.__start_record_callback)


    def __del__(self):
        try:
            self.stop_record()
        except:
            pass


    @property
    def raw_files_dir(self) -> Path | None:
        return self.__raw_files_dir
    

    @raw_files_dir.setter
    def raw_files_dir(self, raw_files_dir: Path | None):
        assert isinstance(raw_files_dir, Path)
        self.__raw_files_dir = raw_files_dir
        self.__raw_files_dir_changed = True


    def __create_data_handlers(self):
        if not self.__raw_files_dir:
            raise ValueError('raw_files_dir is None')

        self.__sensoglove_data_handler = SensogloveDataHandler(
            module=self.__sensoglove_module,
            save_folder_dir=self.__raw_files_dir,
            start_flag=self.__start_flag,
            abort_flag=self.__abort_flag
        )
        self.__is_sensoglove_connected = False

        self.__quattrocento_data_handler = QuattrocentoDataHandler(
            module=self.__quattrocento_module,
            save_folder_dir=self.__raw_files_dir,
            start_flag=self.__start_flag,
            abort_flag=self.__abort_flag,
            quattrocento_settings=self.__quattrocento_settings
        )
        self.__is_quattrocento_connected = False

        self.__raw_files_dir_changed = False


    def __connect_callback(self):
        if self.__raw_files_dir_changed:
            self.__create_data_handlers()

        try:
            if not self.__is_sensoglove_connected:
                self.__is_sensoglove_connected = self.__sensoglove_data_handler.connect_module()
        except:
            self.__is_sensoglove_connected = False
        if self.__is_sensoglove_connected:
            self.__connection_window.change_glove_status('подключено', True)
        else:
            self.__connection_window.change_glove_status('нет подключения', False)

        try:
            if not self.__is_quattrocento_connected:
                self.__is_quattrocento_connected = self.__quattrocento_data_handler.connect_module()
        except:
            self.__is_quattrocento_connected = False
        if self.__is_quattrocento_connected:
            self.__connection_window.change_myogragh_status('подключено', True)
        else:
            self.__connection_window.change_myogragh_status('нет подключения', False)


    def __back_callback(self):
        # TODO: check correction of this method
        try:
            self.__sensoglove_data_handler.stop_record()
        except:
            pass

        try:
            self.__quattrocento_data_handler.stop_record()
        except:
            pass
        
        if not (self.__sensoglove_data_handler.is_ready or self.__quattrocento_data_handler.is_ready): 
            self.__stacked_windows.display_patient_info()
            self.__connection_window.reset()


    def __start_record_callback(self):
        if self.__sensoglove_data_handler.is_ready and self.__quattrocento_data_handler.is_ready:
            self.__quattrocento_data_handler.start()
            self.__sensoglove_data_handler.start()
            self.__abort_flag.clear()
            self.__start_flag.set()
            self.__stacked_windows.display_experiment()
            self.__additional_callback_for_start_record()
    

    def stop_record(self):
        self.__abort_flag.set()
        self.__start_flag.clear()
        self.__quattrocento_data_handler.join()
        self.__sensoglove_data_handler.join()