import sys
sys.path.append('./app')

import os
from pathlib import Path
import h5py

from data.repositories import MarkupDataReader, SensogloveRawDataReader, EMGDataReader, DataMerger


def merge_data_manually(raw_data_dir: str | Path, ready_data_dir: str | Path, ans: str | None = None):
    if not os.path.exists(raw_data_dir):
        raise FileExistsError('Folder with raw file does not exist')
    code, age, gender, hand, date = None, None, None, None, None
    if not os.path.exists(ready_data_dir):
        print('HDF5 file does not exist, so you need to provide some data about the participant')
        while not code or not age or not gender or not hand:
            if not code:
                try:
                    code = int(input('Participant code (int): '))
                except:
                    continue

            if not age:
                try:
                    age = int(input('Participant age (int): '))
                except:
                    continue
            
            if not gender:
                g = input('Participant gender (m/f): ')
                if g not in {'m', 'f'}:
                    continue
                gender = g
            
            if not hand:
                h = input('Participant leading hand (l/r): ')
                if h not in {'l', 'r'}:
                    continue
                hand = h
        
        with h5py.File(ready_data_dir, 'w') as save_file:
            save_file.attrs['participant_code'] = code
            save_file.attrs['participant_age'] = age
            save_file.attrs['participant_gender'] = gender
            save_file.attrs['participant_leading_hand'] = hand
            save_file.attrs['date'] = 'empty'
    
    else:
        with h5py.File(ready_data_dir, 'a') as save_file:
            if len(save_file.keys()) > 0:
                if ans != 'y':
                    ans = input('This file already exists. Would you like to rewrite it? (y/n): ')
                if ans != 'y':
                    return
                
                code = save_file.attrs['participant_code']
                age = save_file.attrs['participant_age']
                gender = save_file.attrs['participant_gender']
                hand = save_file.attrs['participant_leading_hand']
                date = save_file.attrs['date']
        
        os.remove(ready_data_dir)
        with h5py.File(ready_data_dir, 'w') as save_file:
            save_file.attrs['participant_code'] = code
            save_file.attrs['participant_age'] = age
            save_file.attrs['participant_gender'] = gender
            save_file.attrs['participant_leading_hand'] = hand
            save_file.attrs['date'] = date
        


    markup_data = MarkupDataReader(raw_data_dir).load_data()
    sensoglove_data = SensogloveRawDataReader(raw_data_dir).get_valuable_data()
    emg_data = EMGDataReader(raw_data_dir).get_emg_data()
    data_merger = DataMerger(ready_data_dir)
    data_merger.merge_data(
        emg_data=emg_data,
        sensoglove_data=sensoglove_data,
        markup_data=markup_data
    )


if __name__=='__main__':
    raw_data_dir = Path(sys.argv[1])
    ready_data_dir = Path(sys.argv[2])
    merge_data_manually(raw_data_dir, ready_data_dir)
    