import json
from pathlib import Path

from tests import QuattrocentoTest


if __name__=='__main__':
    current_dir = Path()
    
    with open(current_dir / 'settings.json', 'r') as json_file:
        settings = json.load(json_file)
    
    temp_files_dir = current_dir / 'temp'

    test = QuattrocentoTest(settings)
    test.start_test(temp_files_dir, 10)