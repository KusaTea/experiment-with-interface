import json
from pathlib import Path

import numpy as np

import data.models as dtpe


class SensogloveRawDataReader:

    def __init__(self, file_dir: Path):
        self.file_dir = file_dir / 'glove_data.json'

    def read_all_glove_data(self):
        with open(self.file_dir, 'r') as f:
            data = f.readlines()

        return list(
            map(lambda row: json.loads(row.strip()), data)
            )
    
    def get_valuable_data(self) -> dtpe.SensoGloveDataType:
        data: dtpe.SensoGloveDataType = {
            'start': 0,
            'lia': list(),
            'bones': list(),
            'fingers': list(),
            'timestamps': list()
        }
        with open(self.file_dir, 'r') as f:
            while line := f.readline():
                try:
                    line_data = json.loads(line.strip())
                except:
                    continue

                if 'start_time' in line_data:
                    data['start'] = line_data['start_time']
                elif line_data['type'] == 'position':
                    data['lia'].append(self.__transform_lia_data(line_data['data']['fingers']))
                    data['bones'].append(self.__transform_bones_data(line_data['data']['bones']))
                    data['fingers'].append(self.__transform_fingers_data(line_data['data']['fingers']))
                    data['timestamps'].append(int(line_data['data']['ts']))

        data['lia'] = np.array(data['lia'], dtype=np.float32)
        for key in ('bones', 'fingers'):
            data[key] = np.array(data[key], dtype=np.float32)
        data['timestamps'] = np.array(data['timestamps'], dtype=np.int64)

        return data
    
    
    @staticmethod
    def __transform_lia_data(fingers_data: dict):
        finger_lia = list()
        for finger in fingers_data:
            finger_lia.append(finger['lia'])
            try:
                finger_lia.append(finger['lia2'])
            except KeyError:
                continue
        return np.array(finger_lia, dtype=np.float32)
    

    @staticmethod
    def __transform_bones_data(bones_data: dict | list):
        if isinstance(bones_data, dict):
            data = [bones_data[f'bone_{num}'] for num in range(0, 16)]
        else:
            data = [bones_data[start: start + 4] for start in range(0, len(bones_data), 4)]
        return np.array(data, dtype=np.float32)
    

    @staticmethod
    def __transform_fingers_data(fingers_data: dict):
        data = list()
        for finger in fingers_data:
            data.append(finger['quat'])
            try:
                data.append(finger['quat2'])
            except KeyError:
                continue
        return np.array(data, dtype=np.float32)