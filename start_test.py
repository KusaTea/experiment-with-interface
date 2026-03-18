import json
from pathlib import Path

from tests.sensoglove_test import SensoGloveTest


if __name__=='__main__':
    current_dir = Path()
    
    temp_files_dir = current_dir / 'temp'

    with open(current_dir / 'settings.json') as json_file:
        settings = json.load(json_file)

    test = SensoGloveTest(
        temp_folder_dir=temp_files_dir,
        glove_ip_address='127.0.0.1',
        glove_port=53450
    )

    test.start_test(
        test_duration_in_s=10
    )