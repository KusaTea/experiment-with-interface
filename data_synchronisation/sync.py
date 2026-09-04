import h5py
import numpy as np
from pathlib import Path


def sync_data(data_dir: Path, participant_code: int, save_dir: Path):
    emg_data = None
    attrs = dict()
    with h5py.File(data_dir / f'{participant_code}' / f'{participant_code}.hdf5', mode='r') as hdf_file:
        for key in hdf_file.attrs.keys():
            attrs[key] = hdf_file.attrs.get(key)
        emg_data = np.asarray(hdf_file.get('emg')[:], dtype=np.float32)

    markup = np.load(data_dir / f'{participant_code}' / 'markup.npy')

    with h5py.File(save_dir / f'{participant_code}.hdf5', mode='w') as hdf_file:
        for key, value in attrs.items():
            hdf_file.attrs[key] = value
        
        hdf_file.create_dataset('emg', data=emg_data)
        hdf_file.create_dataset('markup', data=markup)


if __name__=='__main__':
    data_dir = Path('./tmp/data')
    save_dir = Path('/home/matthew/datasets/EMG_glove/synced')
    
    for participant_code in range(1, 23):
        print('\n')
        print(participant_code)
        try:
            sync_data(data_dir, participant_code, save_dir)
        except BaseException as e:
            print(e)