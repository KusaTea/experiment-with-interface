import json
from pathlib import Path

import numpy as np

from ..arguments_types import data_types as dtpe


class MarkupDataCreater:

    def __init__(self, file_dir: Path):
        self.save_file = open(file_dir / 'markup.json', 'w')
    
    def __del__(self):
        self.save_file.close()

    def save_data(self, timestamp: str, exercise: int):
        json.dump({timestamp: exercise}, self.save_file)
        self.save_file.write('\n')


class MarkupDataReader:

    def __init__(self, file_dir: Path):

        self.file_dir = file_dir / 'markup.json'

    def load_data(self) -> dtpe.MarkupDataType:
        '''Returns two arrays: timestamps and exercises indeces'''
        data = list()

        with open(self.file_dir, 'r') as f:
            while line := f.readline():
                try:
                    line_data = json.loads(line.strip())
                except:
                    continue

                data += list(line_data.items())
        
        data = np.array(data)
        return {
            'timestamps': data[:, 0].astype(np.float32),
            'exercises': data[:, 1].astype(np.int32)
            }