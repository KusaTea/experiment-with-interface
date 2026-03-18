import h5py
from datetime import datetime
from typing import Literal
from pathlib import Path
import os


class ParticipantData:

    def __init__(self, code: int, age: int, gender: Literal['m', 'f'], hand: Literal['r', 'l']):
        assert code > 0
        assert age > 0
        assert gender in {'m', 'f'}
        assert hand in {'r', 'l'}

        self.code = code
        self.age = age
        self.gender = gender
        self.hand = hand

    def save_participant_info(self, save_dir: Path):
        if not os.path.exists(save_dir / (str(self.code) + '.hdf5')):
            with h5py.File(save_dir / (str(self.code) + '.hdf5'), 'w') as save_file:
                save_file.attrs['participant_code'] = self.code
                save_file.attrs['participant_age'] = self.code
                save_file.attrs['participant_gender'] = self.gender
                save_file.attrs['participant_leading_hand'] = self.hand
                save_file.attrs['date'] = str(datetime.now())
        
        else:
            raise FileExistsError('File for such code already exists')