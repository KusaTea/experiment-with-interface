import socket
import datetime
import multiprocessing
import numpy as np
import time
import datetime
from pathlib import Path

import h5py

from .quattrocento_settings import QuattrocentoSettings


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
                 abort_flag: multiprocessing.Event,
                 start_flag: multiprocessing.Event,
                 ready_flag: multiprocessing.Event,
                 data_save_dir: Path
                 ):
        super().__init__(name='Quattrocento')

        self.ip_port = ip_port
        self.settings = settings
        self.abort_flag = abort_flag
        self.start_flag = start_flag
        self.ready_flag = ready_flag
        self.data_save_dir = data_save_dir

    def __del__(self):
        try:
            self.client.close()
        except:
            pass

    def recieve_data(self, data_group: h5py.Group):
        self.client.send(self.settings())
        
        print('Acquisition in process...')
        
        buffer = b''
        while not (self.abort_flag.is_set()):
            start = str(time.time())
            while len(buffer) < self.settings.buffer_size and not(self.abort_flag.is_set()):
                buffer += self.client.recv(self.settings.buffer_size - len(buffer))
            data = np.frombuffer(buffer[:self.settings.buffer_size], dtype=np.int16).reshape(self.settings.sampling_rate, self.settings.num_of_channels)
            buffer = buffer[self.settings.buffer_size:]
            data_group.create_dataset(name=start, data=data)
    
    def run(self):
        try:
            with h5py.File(self.data_save_dir, 'a', track_order=True) as dataset_file:
                group = dataset_file.create_group("emg")

                group.attrs["sampling_rate"] = self.settings.sampling_rate
                group.attrs["channels_num"] = self.settings.num_of_channels
                group.attrs["mV_constant"] = self.settings.mV_constant
                group.attrs["dtype"] = "int16 (little)"

                data_group = group.create_group("data")

                while not self.start_flag.is_set():
                    time.sleep(0.1)
                self.recieve_data(data_group)
        except BaseException as e:
            print("Quattrocento")
            print(e)
        finally:
            self.stop_listening()

    def make_connect(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(5)
            self.client.connect(self.ip_port)
            self.ready_flag.set()
            return True
        except:
            return False

    def send_stop_command(self):
        self.settings.acquisition_byte = 128
        self.client.send(self.settings())

    def stop_listening(self):
        self.send_stop_command()
        self.client.close()