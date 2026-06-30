import json
from pathlib import Path

import numpy as np

from data.models import MarkupDataType


class MarkupDataCreater:

    def __init__(self, file_dir: Path):
        self.save_file = open(file_dir / 'markup.json', 'w')
    
    def close_file(self):
        self.save_file.close()

    def __del__(self):
        try:
            self.save_file.close()
        except:
            pass

    def save_data(self, timestamp: str, exercise: int):
        json.dump({timestamp: exercise}, self.save_file)
        self.save_file.write('\n')


class MarkupDataReader:

    def __init__(self, file_dir: Path):

        self.file_dir = file_dir / 'markup.json'

    def load_data(self) -> MarkupDataType:
        '''Returns two arrays: timestamps and exercises indeces'''
        timestamps = list()
        exercises = list()

        with open(self.file_dir, 'r') as f:
            while line := f.readline():
                try:
                    line_data = json.loads(line.strip())
                except:
                    continue

                timestamps.append((list(line_data.keys()))[0])
                exercises.append((list(line_data.values()))[0])

        return {
            'timestamps': np.array(timestamps, dtype=np.float64),
            'exercises': np.array(exercises, dtype=np.int8)
            }