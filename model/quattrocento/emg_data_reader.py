import h5py
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from ..arguments_types.data_types import EMGDataType


class EMGDataReader:

    def __init__(self, raw_data_files_dir: Path):
        self.__data_dir = raw_data_files_dir / 'emg.hdf5'

        self.__hdf_file = h5py.File(self.__data_dir, 'r')
        self.__num_of_channels = self.__hdf_file.attrs['num_of_channels']
        self.__sampling_rate = self.__hdf_file.attrs['sampling_rate']
        self.__mV_constant = self.__hdf_file.attrs['mV_constant']
        self.__keys = list(self.__hdf_file.keys())

        self.__iter_counter = 0


    def __del__(self):
        self.close_file()

    
    def __len__(self) -> int:
        return len(self.__hdf_file.keys())


    def __iter__(self):
        return self
    

    def __next__(self):
        if self.__iter_counter < len(self):
            ts = self.__keys[self.__iter_counter]
            return float(ts), np.array(self.__hdf_file.get(ts)).reshape(self.__sampling_rate, self.__num_of_channels)
        
        else:
            raise StopIteration


    def close_file(self):
        try:
            self.__hdf_file.close()
        except:
            pass


    def get_all_timestamps(self) -> NDArray:
        return np.array([float(ts) for ts in self.__hdf_file.keys()], dtype=np.float32)
    

    def get_all_emg_data(self):
        data = list()
        for ts in self.__hdf_file.keys():
            emg_data = np.array(self.__hdf_file.get(ts)).reshape(self.__sampling_rate, self.__num_of_channels)

            data.append(emg_data)

        return np.array(data)
    

    def get_emg_data(self) -> EMGDataType:
        return {
            'timestamps': self.get_all_timestamps(),
            'emg': self.get_all_emg_data(),
            'mV_constant': self.__mV_constant
            }


    @property
    def mV_constant(self) -> int:
        return self.__mV_constant