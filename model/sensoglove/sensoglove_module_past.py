import socket
import json
import time
from pathlib import Path

import multiprocessing
from multiprocessing.synchronize import Event


class SensoGloveException(Exception):
    pass


class AppSensoGloveClient(multiprocessing.Process):
    '''This class is using TCP connection'''
    def __init__(
            self,
            save_dir: Path,
            start_flag: Event,
            ready_flag: Event,
            abort_flag: Event,
            ip_address: str = "127.0.0.1",
            port: int = 53450
            ):
        super().__init__(name='SensoGlove')
        
        self.save_dir = save_dir / 'glove_data.json'

        self.glove_socket = socket.socket()
        self.ip_port = (ip_address, port)

        self.start_flag = start_flag
        self.ready_flag = ready_flag
        self.abort_flag = abort_flag
    

    def __del__(self):
        try:
            self.close_connection()
        except:
            pass


    def glove_recv(self, timeout: float = 1):
        self.glove_socket.settimeout(timeout)

        try:
            data = self.glove_socket.recv(60000)
            try:
                return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                return data
            
        except TimeoutError:
            raise SensoGloveException('Timeout of data receiving')
        except Exception as e:
            return SensoGloveException(str(e))
    

    def check_app_connection(self):
        answer = None
        while not isinstance(answer, dict) or "data" not in answer:
            answer = self.glove_recv(1)


    def make_connect(self):
        try:
            self.glove_socket.settimeout(5)
            self.glove_socket.connect(self.ip_port)
            self.check_app_connection()
            self.ready_flag.set()
        except TimeoutError:
            print(SensoGloveException('Timeout of connection'))
            self.ready_flag.clear()
        except ConnectionRefusedError:
            print(SensoGloveException('Connection error'))
            self.ready_flag.clear()
    

    def get_data(self):
        with open(self.save_dir, 'w') as save_file:
            json.dump({"start_time": time.time()}, save_file)
            save_file.write('\n')
            while not self.abort_flag.is_set():
                    try:     
                        response = self.glove_recv(1)
                        if isinstance(response, dict) and "data" in response:
                            json.dump(response, save_file)
                            save_file.write('\n')
                    except SensoGloveException:
                        continue
                    except KeyboardInterrupt:
                        break
    

    def run(self):
        try:
            while not self.start_flag.is_set() and not self.abort_flag.is_set():
                continue
            self.get_data()

        finally:
            self.close_connection()

    
    def close_connection(self):
        self.glove_socket.shutdown(socket.SHUT_RDWR)
        self.glove_socket.close()
        self.ready_flag.clear()