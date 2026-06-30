from pathlib import Path
from typing import Any

import h5py
from numpy.typing import NDArray


class DataReader:
    def __init__(self, timestamps: h5py.Dataset, values: h5py.Dataset):
        self.timestamps = timestamps
        self.values = values

    @property
    def shape(self):
        return self.values.shape

    def __len__(self):
        return self.values.shape[0]

    def __getitem__(self, data_slice) -> tuple[NDArray, NDArray]:
        return self.timestamps[data_slice], self.values[data_slice]


class EMGDataReader(DataReader):
    def __init__(self, timestamps: h5py.Dataset, values: h5py.Dataset, mV_constant: float):
        super().__init__(timestamps, values)
        self.mV_constant = mV_constant

    def __getitem__(self, data_slice) -> tuple[NDArray, NDArray]:
        timestamps, values = super().__getitem__(data_slice)
        return timestamps, values * self.mV_constant


class ExperimentDataReader:
    """Reader for final experiment HDF5 files."""

    PARTICIPANT_ATTRS = (
        "participant_code",
        "participant_age",
        "participant_gender",
        "participant_leading_hand",
        "date",
    )

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self._file = h5py.File(self.file_path, "r")

    def close(self):
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def show_groups(self) -> list[str]:
        """Print and return all root groups stored in the file."""
        groups = [name for name, item in self._file.items() if isinstance(item, h5py.Group)]
        for group in groups:
            print(group)
        return groups

    def get_participant_info(self) -> dict[str, Any]:
        return {
            attr_name: self._decode_value(self._file.attrs[attr_name])
            for attr_name in self.PARTICIPANT_ATTRS
            if attr_name in self._file.attrs
        }

    def get_emg_data(self) -> EMGDataReader:
        group = self._file["emg"]
        return EMGDataReader(group["timestamps"], group["emg"], group.attrs["mV_constant"])

    def get_markup_data(self) -> DataReader:
        return self._get_group_reader("markup", "exercises")

    def get_imu_data(self) -> DataReader:
        return self._get_group_reader("position", "imu")

    def get_hand_quaternions(self) -> DataReader:
        return self._get_group_reader("position", "fingers")

    def get_bones_quaternions(self) -> DataReader:
        return self._get_group_reader("position", "bones")

    def _get_group_reader(
        self,
        group_name: str,
        values_name: str,
    ) -> DataReader:
        group = self._file[group_name]
        return DataReader(group["timestamps"], group[values_name])

    @staticmethod
    def _decode_value(value):
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value
