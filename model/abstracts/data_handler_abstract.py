from pathlib import Path
from abc import ABC, abstractmethod
from multiprocessing.synchronize import Event

from .module_abstract import ModuleAbstract


class DataHandlerAbstract(ABC):

    def __init__(
        self,
        module: ModuleAbstract,
        save_folder_dir: Path,
        start_flag: Event,
        abort_flag: Event
        ):
        self.__module = module
        self.__save_file_dir = save_folder_dir
        self.__start_flag = start_flag
        self.__abort_flag = abort_flag
    

    @property
    @abstractmethod
    def is_ready(self) -> bool:
        # return self.__module.check_connection()
        pass


    @abstractmethod
    def start_record(self):
        # open and set up file
        # (optional) send start command to the module
        # while not self.__abort_flag.is_set():
        # get data
        # save data
        # add try...except construction
        pass


    @abstractmethod
    def stop_record(self):
        # (optional) send stop command to the module
        # self.__module.close_connection()
        # check self.__module.is_connected()
        pass


    @abstractmethod
    def connect_module(self) -> bool:
        # self.__module.connect()
        # self.__module.check_connection()
        pass


    @abstractmethod
    def run(self):
        # while not start_flag.is_set()
        #   continue
        # self.start_record()
        # self.stop_record()
        pass
    