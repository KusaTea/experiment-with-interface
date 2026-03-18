import socket
from select import select
import json

from ..abstracts import ModuleAbstract


class SensogloveException(Exception):
    pass


class SensogloveModule(ModuleAbstract):

    def __init__(
        self,
        ip_address: str,
        port: int
    ):
        self.__ip_address = ip_address
        self.__port = port
        self.__connected = False

    
    @property
    def is_connected(self):
        return self.__connected


    def connect(self):
        self.__client = socket.socket()
        self.__client.settimeout(5)

        try:
            self.__client.connect((self.__ip_address, self.__port))
        except BaseException as e:
            raise SensogloveException(e)

        self.__client.setblocking(True)
        self.__connected = True


    def send_data(self, data):
        '''You cannot send data to glove'''
        pass
    

    def receive_data(self, timeout: int) -> dict | None:
        ready = select([self.__client], [], [], timeout)
        if ready[0]:
            try:
                return json.loads(self.__client.recv(60000))
            except json.JSONDecodeError:
                return None
        else:
            return None
    

    def close_connection(self):
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