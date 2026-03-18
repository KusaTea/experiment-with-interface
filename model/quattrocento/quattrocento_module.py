import socket
from select import select

import numpy as np
from numpy.typing import NDArray

from ..abstracts import ModuleAbstract


class QuattrocentoModuleException(Exception):
    pass


class QuattrocentoModule(ModuleAbstract):

    def __init__(
        self,
        ip_address: str,
        port: int,
        buffer_size: int
    ):
        self.__ip_address = ip_address
        self.__port = port
        self.__connected = False

        self.__buffer = b''
        self.__buffer_size = buffer_size
    

    @property
    def is_connected(self):
        return self.__connected


    @property
    def buffer_size(self) -> int:
        return self.__buffer_size


    @buffer_size.setter
    def buffer_size(self, buffer_size: int):
        assert buffer_size > 0, 'Buffer size should be greater than 0'
        self.__buffer_size = buffer_size


    def connect(self):
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.settimeout(5)

        try:
            self.__client.connect((self.__ip_address, self.__port))
        except BaseException as e:
            raise QuattrocentoModuleException(e)
        
        self.__client.setblocking(True)
        self.__connected = True


    def send_data(self, data):
        try:
            self.__client.sendall(data)
        except BaseException as e:
            raise QuattrocentoModuleException(e)
    

    def receive_data(self, timeout: int) -> NDArray:
        '''
        ATTENTION: to get data from Quattrocento the starting string
        should be sent to it
        '''
        error_counter = 0
        while len(self.__buffer) < self.__buffer_size:
            ready = select([self.__client], [], [], timeout)
            if ready[0]:
                self.__buffer += self.__client.recv(self.__buffer_size - len(self.__buffer))
            else:
                error_counter += 1
            
            if error_counter > 4:
                raise QuattrocentoModuleException('Timeout of data receiving')
        
        data = np.frombuffer(self.__buffer[:self.__buffer_size], dtype=np.int16)
        self.__buffer = self.__buffer[self.__buffer_size:]
        
        return data
    

    def close_connection(self):
        '''
        ATTENTION: before closing the connection send a stop command to Quattrocento
        '''
        try:
            self.__client.shutdown(socket.SHUT_RDWR)
            self.__client.close()
        except:
            pass

        self.__connected = False


    def check_connection(self) -> bool:
        try:
            self.receive_data(1)
        except BaseException:
            return False
        
        return True
                

