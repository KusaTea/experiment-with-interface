from pathlib import Path
from typing import Any

import h5py
import numpy as np
from numpy.typing import NDArray


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

    def get_emg_data(self, data_slice: slice = slice(None)) -> tuple[NDArray, NDArray]:
        timestamps, emg = self._get_group_data("emg", "emg", data_slice)
        mV_constant = self._file["emg"].attrs["mV_constant"]
        return timestamps, emg * mV_constant

    def get_markup_data(self, data_slice: slice = slice(None)) -> tuple[NDArray, NDArray]:
        return self._get_group_data("markup", "exercises", data_slice)

    def get_imu_data(self, data_slice: slice = slice(None)) -> tuple[NDArray, NDArray]:
        return self._get_group_data("position", "imu", data_slice)

    def get_hand_quaternions(self, data_slice: slice = slice(None)) -> tuple[NDArray, NDArray]:
        return self._get_group_data("position", "fingers", data_slice)

    def get_bones_quaternions(self, data_slice: slice = slice(None)) -> tuple[NDArray, NDArray]:
        return self._get_group_data("position", "bones", data_slice)

    def _get_group_data(
        self,
        group_name: str,
        data_name: str,
        data_slice: slice,
    ) -> tuple[NDArray, NDArray]:
        group = self._file[group_name]
        return np.array(group["timestamps"][data_slice]), np.array(group[data_name][data_slice])

    @staticmethod
    def _decode_value(value):
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value
