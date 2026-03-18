import multiprocessing as mlp
from multiprocessing.synchronize import Event
from pathlib import Path
import json

from ..abstracts import DataHandlerAbstract, ModuleAbstract



class SensogloveDataHandler(DataHandlerAbstract, mlp.Process):

    def __init__(
            self,
            module: ModuleAbstract,
            save_folder_dir: Path,
            start_flag: Event,
            abort_flag: Event
    ):
        mlp.Process.__init__(self)
        self.__module = module
        self.__save_file_dir = save_folder_dir / 'glove_data.json'
        self.__start_flag = start_flag
        self.__abort_flag = abort_flag


    @property
    def is_ready(self) -> bool:
        return self.__module.check_connection()


    def start_record(self):
        try:
            with open(self.__save_file_dir, mode='w') as save_file:
                while not self.__abort_flag.is_set():
                    data = self.__module.receive_data(5)
                    if data and 'data' in data:
                        json.dump(data, save_file)
                        save_file.write('\n')
                        
        except BaseException as e:
            self.__abort_flag.set()
            raise e


    def stop_record(self):
        self.__module.close_connection()
        
        if self.__module.is_connected:
            raise ConnectionError('Couldn\'t stop the connection')


    def run(self):
        try:
            self.__module.connect()
        except BaseException as e:
            self.__abort_flag.set()
            raise e

        while not self.__start_flag.is_set():
            try:
                self.__module.receive_data(0)
            except:
                continue
        
        self.start_record()
        self.stop_record()
