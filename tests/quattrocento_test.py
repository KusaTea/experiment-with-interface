from pathlib import Path
from time import sleep, time
import multiprocessing as mlp

from model.quattrocento import QuattrocentoModule, QuattrocentoDataHandler, QuattrocentoSettings


class QuattrocentoTest:

    def __init__(self, settings):
        self.settings = settings


    def start_test(self, temp_files_dir: Path, test_duration_in_s: int):
        abort_flag = mlp.Event()
        start_flag = mlp.Event()

        quattrocento_settings = QuattrocentoSettings(self.settings['myograph_settings']['options'])

        quattrocento_module = QuattrocentoModule(
            ip_address=self.settings['myograph_settings']['ip'],
            port=self.settings['myograph_settings']['port'],
            buffer_size=quattrocento_settings.buffer_size
        )

        data_handler = QuattrocentoDataHandler(
            module=quattrocento_module,
            save_folder_dir=temp_files_dir,
            start_flag=start_flag,
            abort_flag=abort_flag,
            quattrocento_settings=quattrocento_settings
        )

        data_handler.start()
            
        print('Connection was made')
        print('Process was started')

        start_flag.set()
        start = time()
        while time() - start < test_duration_in_s:
            sleep(1)

        if abort_flag.is_set():
            print('Fail')

        else:
            abort_flag.set()
            print('Success')