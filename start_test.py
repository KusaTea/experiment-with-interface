import json
from pathlib import Path

from tests import SensoGloveTest


if __name__=='__main__':
    current_dir = Path()
    
    temp_files_dir = current_dir / 'temp'

    test = SensoGloveTest(
        temp_folder_dir=temp_files_dir,
        glove_ip_address='127.0.0.1',
        glove_port=53450
    )

    test.start_test()