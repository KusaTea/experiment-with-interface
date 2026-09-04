from pathlib import Path
import h5py
import shutil
import json

import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import rfft, rfftfreq

from modules import EMGPreprocessing, GloveDataPreprocessing, MarkupDataPreprocessing

DPI = plt.rcParams['figure.dpi']


def prep_data(initial_file_dir, save_file_dir):
    emg_preprocesser = EMGPreprocessing(
        file_dir=initial_file_dir,
        channels_slice=channels_slice
    )
    emg_preprocesser()
    
    
    markup_preprocesser = MarkupDataPreprocessing(initial_file_dir)
    markup_preprocesser()
    
    
    glove_preprocesser = GloveDataPreprocessing(
        file_dir=initial_file_dir,
        required_sampling_rate=1024
    )
    glove_preprocesser()
    
    
    with h5py.File(save_file_dir, mode='w') as hdf_file:
        hdf_file.create_dataset('emg', data=emg_preprocesser.emg_data)
        hdf_file.create_dataset('markup', data=markup_preprocesser.exercises)
        hdf_file.create_dataset('repeats', data=markup_preprocesser.repeats)
        hdf_file.create_dataset('lia', data=glove_preprocesser.lia_data)
        hdf_file.create_dataset('lia_norm', data=glove_preprocesser.lia_norm)
    
    del emg_preprocesser, markup_preprocesser, glove_preprocesser


if __name__=='__main__':
    initial_data_dir = Path('/home/matthew/datasets/EMG_glove')
    
    tmp_folder = Path('./tmp')
    tmp_folder.mkdir(parents=True, exist_ok=True)
    
    channels_slice = slice(64, 192)

    work_mode = None
    while not work_mode in {'one', 'several'}:
        work_mode = input('Choose mode (one/several): ')

    if work_mode == 'one':
        participant_code = input('Participant code: ')
        file_name = participant_code + '.hdf5'

        plots_folder = tmp_folder / 'plots' / file_name.split('.')[0]
        plots_folder.mkdir(parents=True, exist_ok=True)
        
        data_folder = tmp_folder / 'data' / file_name.split('.')[0]
        data_folder.mkdir(parents=True, exist_ok=True)

        prep_data(
            initial_file_dir=initial_data_dir / file_name,
            save_file_dir=data_folder / file_name
        )

    else:
        start = int(input('First participant code: '))
        end = int(input('Last participant code: '))

        for participant_code in range(start, end + 1):
            try:
                file_name = str(participant_code) + '.hdf5'
    
                plots_folder = tmp_folder / 'plots' / file_name.split('.')[0]
                plots_folder.mkdir(parents=True, exist_ok=True)
                
                data_folder = tmp_folder / 'data' / file_name.split('.')[0]
                data_folder.mkdir(parents=True, exist_ok=True)
        
                prep_data(
                    initial_file_dir=initial_data_dir / file_name,
                    save_file_dir=data_folder / file_name
                )
            
            except BaseException as e:
                print(participant_code)
                print(e)
                continue