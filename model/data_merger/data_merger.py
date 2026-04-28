import h5py
from pathlib import Path

from ..arguments_types import data_types as dtpe


class DataMerger:

    def __init__(self, save_dir: Path):
        self.save_dir = save_dir

    def merge_data(self, emg_data: dtpe.EMGDataType, sensoglove_data: dtpe.SensoGloveDataType, markup_data: dtpe.MarkupDataType):
        with h5py.File(self.save_dir, 'a') as save_file:
            emg_group = save_file.create_group('emg')
            emg_group.attrs['mV_constant'] = emg_data['mV_constant']
            emg_group.create_dataset('timestamps', data=emg_data['timestamps'])
            emg_group.create_dataset('emg', data=emg_data['emg'])

            position_group = save_file.create_group('position')
            position_group.attrs['start_timestamp'] = sensoglove_data['start']
            position_group.create_dataset(name='imu', data=sensoglove_data['imu'])
            position_group.create_dataset(name='bones', data=sensoglove_data['bones'])
            position_group.create_dataset(name='fingers', data=sensoglove_data['fingers'])
            position_group.create_dataset(name='timestamps', data=sensoglove_data['timestamps'])

            markup_group = save_file.create_group('markup')
            markup_group.create_dataset(name='timestamps', data=markup_data['timestamps'])
            markup_group.create_dataset(name='exercises', data=markup_data['exercises'])
            