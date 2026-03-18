from pathlib import Path
import multiprocessing as mlp
from time import sleep, time

from model.sensoglove import SensogloveModule, SensogloveDataHandler, SensogloveRawDataReader


class SensoGloveTest:

    def __init__(
            self,
            temp_folder_dir: Path,
            glove_ip_address: str,
            glove_port: int
            ):
        
        self.start_flag = mlp.Event()
        self.abort_flag = mlp.Event()

        self.sensoglove_module = SensogloveModule(
            ip_address=glove_ip_address,
            port=glove_port
        )

        self.data_handler = SensogloveDataHandler(
            module=self.sensoglove_module,
            save_folder_dir=temp_folder_dir,
            abort_flag=self.abort_flag,
            start_flag=self.start_flag
        )

        self.data_reader = SensogloveRawDataReader(file_dir=temp_folder_dir)
    

    def start_test(self, test_duration_in_s: int):
        self.data_handler.start()
        print('Connected')

        self.start_flag.set()
        print('Process started')

        start = time()
        while time() - start < test_duration_in_s:
            sleep(0.1)
        
        if self.abort_flag.is_set():
            print('Fail')
        else:
            self.abort_flag.set()
            print('Success')

        print(self.data_reader.get_valuable_data())