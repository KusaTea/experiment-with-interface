from pathlib import Path
from time import sleep, time
import multiprocessing as mlp

from model.quattrocento import QuattrocentoClient, QuattrocentoSettings


class QuattrocentoTest:

    def __init__(self, settings):
        self.settings = settings


    def start_test(self, temp_files_dir: Path, test_duration_in_s: int):
        abort_flag = mlp.Event()
        start_flag = mlp.Event()
        ready_flag = mlp.Event()

        quattrocento_settings = QuattrocentoSettings(self.settings['myograph_settings']['options'])

        quattrocento_client = QuattrocentoClient(
            ip_port=(self.settings['myograph_settings']['ip'], self.settings['myograph_settings']['port']),
            settings=quattrocento_settings,
            abort_flag=abort_flag,
            start_flag=start_flag,
            ready_flag=ready_flag,
            data_save_dir=temp_files_dir / 'quattrocento.hdf5'
        )

        try:
            if not quattrocento_client.make_connect():
                raise Exception('Connection was failed')
            
            print('Connection was made')

            while not ready_flag.is_set():
                sleep(1)

            quattrocento_client.start()
            print('Process was started')

            start_flag.set()
            start = time()
            while time() - start < test_duration_in_s:
                sleep(1)

        finally:
            abort_flag.set()
            print('Abort flag was set')
            try:
                quattrocento_client.join(10)
            except TimeoutError:
                quattrocento_client.terminate()
            except AssertionError:
                pass
            quattrocento_client.close()