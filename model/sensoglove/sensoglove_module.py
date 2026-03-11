import socket
import json
import time
from pathlib import Path

import multiprocessing


class AppSensoGloveClient(multiprocessing.Process):
    '''This class is using TCP connection'''
    def __init__(
            self,
            save_dir: Path,
            start_flag: multiprocessing.Event,
            ready_flag: multiprocessing.Event,
            abort_flag: multiprocessing.Event,
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
        self.close_connection()

    def glove_recv(self, timeout: float = 1):
        self.glove_socket.settimeout(timeout)
        try:
            data = self.glove_socket.recv(60000)
            try:
                return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                return data
        except socket.timeout:
            print("SensoGlove: Timeout of data receiving")
            return None
        except BlockingIOError:
            print("SensoGlove: BlockingIOError")
            return None
        except Exception as e:
            print(f"SensoGlove: Receive error: {e}")
            return None
    
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
            return True
        except:
            return False
    
    def get_data(self):
        with open(self.save_dir, 'w') as save_file:
            json.dump({"start_time": time.time()}, save_file)
            save_file.write('\n')
            while not self.abort_flag.is_set():
                    try:     
                        response = self.glove_recv(0.1)
                        if isinstance(response, dict) and "data" in response:
                            json.dump(response, save_file)
                            save_file.write('\n')
                    except KeyboardInterrupt:
                        break
    
    def run(self):
        try:
            while not self.start_flag.is_set():
                continue
            self.get_data()

        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print("SensoGlove")
            print(f"Error: {e}")
        finally:
            print("Disconnecting...")
            self.close_connection()

    
    def close_connection(self):
        self.glove_socket.close()