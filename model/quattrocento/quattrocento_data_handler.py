import multiprocessing as mlp
from multiprocessing.synchronize import Event
from pathlib import Path
import h5py
from time import time

from model.abstracts.module_abstract import ModuleAbstract

from ..abstracts import DataHandlerAbstract
from .quattrocento_settings import QuattrocentoSettings


class QuattrocentoDataHandler(DataHandlerAbstract, mlp.Process):

    def __init__(
            self,
            module: ModuleAbstract,
            save_folder_dir: Path,
            start_flag: Event,
            abort_flag: Event,
            quattrocento_settings: QuattrocentoSettings
        ):
        mlp.Process.__init__(self)
        self.__module = module
        self.__save_file_dir = save_folder_dir / 'emg.hdf5'
        self.__start_flag = start_flag
        self.__abort_flag = abort_flag
        self.__settings = quattrocento_settings

        self.__is_ready = False


    @property
    def is_ready(self) -> bool:
        return self.__is_ready

    
    def __check_module_connection(self):
        try:
            self.__module.send_data(self.__settings.get_bytes())
            self.__is_ready =  self.__module.check_connection()

        except BaseException:
            self.__is_ready = False
        
        finally:
            self.__module.send_data(self.__settings.get_stop_command_bytes())



    def start_record(self):
        with h5py.File(self.__save_file_dir, mode='w') as save_file:
            save_file.attrs['sampling_rate'] = self.__settings.sampling_rate
            save_file.attrs['num_of_channels'] = self.__settings.num_of_channels
            save_file.attrs["mV_constant"] = self.__settings.mV_constant
            save_file.attrs['readme'] = 'data should be reshaped (sampling_rate, num_of_channels); each value must bu multiplied by mV_constant'

            self.__module.send_data(self.__settings.get_bytes())
            
            while not self.__abort_flag.is_set():
                try:
                    data = self.__module.receive_data(2)
                    ts = str(time())

                    save_file.create_dataset(
                        name=ts,
                        data=data
                        )
                except BaseException as e:
                    self.__abort_flag.set()
                    raise e


    def stop_record(self):
        self.__module.send_data(self.__settings.get_stop_command_bytes())
        self.__module.close_connection()
        
        if self.__module.is_connected:
            raise ConnectionError('Couldn\'t stop the connection')

        self.__is_ready = False


    def connect_module(self) -> bool:
        try:
            self.__module.connect()
            self.__check_module_connection()
            return self.__is_ready
        except BaseException as e:
            self.__abort_flag.set()
            raise e


    def run(self):
        if not self.__is_ready:
            self.connect_module()

        while not self.__start_flag.is_set():
            continue

        self.start_record()
        self.stop_record()