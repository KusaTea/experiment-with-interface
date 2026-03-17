from pathlib import Path
import multiprocessing as mlp
from time import sleep, time

from model.sensoglove import AppSensoGloveClient
from model.sensoglove import SensoGloveRawDataReader


class SensoGloveTest:

    def __init__(
            self,
            temp_folder_dir: Path,
            glove_ip_address: str,
            glove_port: int
            ):
        
        self.ready_flag = mlp.Event()
        self.start_flag = mlp.Event()
        self.abort_flag = mlp.Event()

        self.sensoglove_client = AppSensoGloveClient(
            save_dir=temp_folder_dir,
            start_flag=self.start_flag,
            ready_flag=self.ready_flag,
            abort_flag=self.abort_flag,
            ip_address=glove_ip_address,
            port=glove_port
        )

        self.data_reader = SensoGloveRawDataReader(file_dir=temp_folder_dir)
    

    def start_test(self):
        try:
            if not self.sensoglove_client.make_connect():
                raise Exception('Connection was failed')
            
            print('Connection was made')

            while not self.ready_flag:
                sleep(1)

            self.sensoglove_client.start()
            print('Process was started')
            self.start_flag.set()

            start = time()
            while time() - start < 5:
                sleep(0.5)
            
            self.abort_flag.set()
            print('Abort flag was set')

        except BaseException as e:
            self.abort_flag.set()
            print(e)

        try:
            self.sensoglove_client.join(10)
        except TimeoutError:
            self.sensoglove_client.terminate()
        except AssertionError:
            pass
        self.sensoglove_client.close()


        print(self.data_reader.get_valuable_data())