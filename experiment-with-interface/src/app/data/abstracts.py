from pathlib import Path
from abc import ABC, abstractmethod
from multiprocessing.synchronize import Event
from typing import Any


class ModuleAbstract(ABC):

    def __init__(
            self,
            ip_address: str,
            port: int
    ):
        self.__ip_address = ip_address
        self.__port = port
        self.__connected = False
    

    @property
    @abstractmethod
    def is_connected(self):
        return self.__connected


    @abstractmethod
    def connect(self):
        # create a socket object
        # set timout
        # connect to a server via ip and port
        # should contain try...except construction for timeout and connection error
        # remove timeout
        # self.__connected = True
        pass


    @abstractmethod
    def send_data(self, data):
        # send data to socket
        pass
    

    @abstractmethod
    def receive_data(self, timeout: int) -> Any:
        # request data
        # return data
        # should contain try...except construction for timeout and ValueError
        pass
    

    @abstractmethod
    def close_connection(self):
        # shutdown socket
        # close socket
        # should contain try...except construction for timeout and ValueError
        # self.__connected = False 
        pass


    @abstractmethod
    def check_connection(self) -> bool:
        # try to receive data
        # return True if connection is stable also False
        pass


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
    