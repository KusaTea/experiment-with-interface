import socket
import multiprocessing
from multiprocessing.synchronize import Event
import numpy as np
import time
from pathlib import Path
from select import select
from copy import deepcopy

import h5py

from .quattrocento_settings import QuattrocentoSettings


class QuattrocentoError(Exception):
    pass


class QuattrocentoClient(multiprocessing.Process):
    '''
    Connection is performed through TCP port using socket module.
    
    To start the system, you need to send a string of bytes. Configuration is performed using 40 bytes.
    Bytes 4-39 configure the input channels. The last byte is a CRC8 error check.
    For more information, see the configuration document.

    After receiving the start command, the device begins sending data as a sequence of bytes.
    The values ​​consist of two bytes (short).
    The total number of bytes transmitted per second is calculated using the formula:
    number of channels * sampling rate * 2 (since the values ​​are short (int16))

    At the end of recording, you must send a string of bytes to the device with the first byte equal to 128.
    Otherwise, Quattrocento will continue recording, which may cause desynchronization with the device.

    Data is saved to .hdf5 file.
    '''
    def __init__(self,
                 ip_port: tuple,
                 settings: QuattrocentoSettings,
                 abort_flag: Event,
                 start_flag: Event,
                 ready_flag: Event,
                 data_save_dir: Path
                 ):
        super().__init__(name='Quattrocento')

        self.ip_port = ip_port
        self.settings = settings
        self.abort_flag = abort_flag
        self.start_flag = start_flag
        self.ready_flag = ready_flag
        self.data_save_dir = data_save_dir

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5)


    def recieve_data(self, bufsize: int) -> bytes:
        try:
            ready = select([self.client], [], [], 10)
            if ready[0]:
                return self.client.recv(bufsize)
            else:
                raise TimeoutError()

        except TimeoutError:
            raise QuattrocentoError('Timeout of data receiving')
        

    def send_data(self, data):
        try:
            self.client.sendall(data)
        except TimeoutError:
            raise QuattrocentoError('Timeout of data sending')
            


    def recieve_data_process(self, data_group: h5py.Group):
        self.send_data(self.settings.get_bytes())
        
        buffer = b''
        while not self.abort_flag.is_set():
            ts = str(time.time())

            while len(buffer) < self.settings.buffer_size and not self.abort_flag.is_set():
                buffer += self.recieve_data(self.settings.buffer_size - len(buffer))

            if len(buffer) >= self.settings.buffer_size:
                data = np.frombuffer(buffer[:self.settings.buffer_size], dtype=np.int16).reshape(self.settings.sampling_rate, self.settings.num_of_channels)
                buffer = buffer[self.settings.buffer_size:]

                data_group.create_dataset(name=ts, data=data)
    

    def get_demo_data(self):
        try:
            self.send_data(self.settings.get_bytes())
            self.recieve_data(self.settings.buffer_size)
        finally:
            self.send_stop_command()

    
    def run(self):
        try:
            with h5py.File(self.data_save_dir, 'a', track_order=True) as dataset_file:
                try:
                    group = dataset_file.create_group("emg")
                except ValueError:
                    del dataset_file['emg']
                    group = dataset_file.create_group("emg")

                group.attrs["sampling_rate"] = self.settings.sampling_rate
                group.attrs["channels_num"] = self.settings.num_of_channels
                group.attrs["mV_constant"] = self.settings.mV_constant
                group.attrs["dtype"] = "int16 (little)"

                data_group = group.create_group("data")

                while not self.start_flag.is_set():
                    time.sleep(0.1)

                self.recieve_data_process(data_group)
        
        finally:
            self.stop_listening()


    def make_connect(self) -> bool:
        try:
            self.client.connect(self.ip_port)
            self.client.setblocking(True)
            self.get_demo_data()
            self.ready_flag.set()
            return True
        except BaseException as e:
            print(e)
            return False


    def send_stop_command(self):
        turn_off_settings = deepcopy(self.settings)
        turn_off_settings.acquisition_byte = 128
        self.send_data(turn_off_settings.get_bytes())


    def stop_listening(self):
        self.send_stop_command()
        self.client.shutdown(socket.SHUT_RDWR)
        self.client.close()