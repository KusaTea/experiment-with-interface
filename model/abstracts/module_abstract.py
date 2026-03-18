from abc import ABC, abstractmethod
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