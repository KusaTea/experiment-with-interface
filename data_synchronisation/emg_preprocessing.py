from pathlib import Path
from typing import Any

import h5py
import numpy as np
from numpy.typing import NDArray
from scipy import signal


class EMGPreprocessing:
    def __init__(
        self,
        file_dir: str | Path,
        channels_slice: slice | list[int] | NDArray[Any],
        requred_sampling_rate: int,
        lower_frequency_threshold: float,
        higher_frequency_threshold: float,
    ):
        self.file_dir = Path(file_dir)
        self.channels_slice = channels_slice
        self.requred_sampling_rate = requred_sampling_rate
        self.required_sampling_rate = requred_sampling_rate
        self.lower_frequency_threshold = lower_frequency_threshold
        self.higher_frequency_threshold = higher_frequency_threshold

        self.initial_sampling_rate: int | None = None
        self.emg_data: NDArray[np.float64] | None = None
        self.timestamps: NDArray[np.float64] | None = None

    def extract_emg_data(self) -> NDArray[np.float64]:
        with h5py.File(self.file_dir, "r") as hdf_file:
            emg_group = hdf_file["emg"]
            emg_dataset = emg_group["emg"]

            self.initial_sampling_rate = self._extract_initial_sampling_rate(
                hdf_file,
                emg_group,
                emg_dataset,
            )

            mV_constant = emg_group.attrs.get(
                "mV_constant",
                hdf_file.attrs.get("mV_constant", 1.0),
            )

            emg_data = self._read_selected_channels(emg_dataset)

        self.emg_data = np.asarray(emg_data, dtype=np.float64) * float(mV_constant)
        return self.emg_data

    def filter_emg(self) -> NDArray[np.float64]:
        self._ensure_emg_data()
        self._ensure_initial_sampling_rate()

        nyquist_frequency = self.initial_sampling_rate / 2
        if self.higher_frequency_threshold >= nyquist_frequency:
            raise ValueError(
                "higher_frequency_threshold must be lower than the Nyquist frequency."
            )

        notch_b, notch_a = signal.iirnotch(
            w0=50,
            Q=30,
            fs=self.initial_sampling_rate,
        )
        filtered_data = signal.filtfilt(notch_b, notch_a, self.emg_data, axis=0)

        sos = signal.butter(
            N=4,
            Wn=[self.lower_frequency_threshold, self.higher_frequency_threshold],
            btype="bandpass",
            fs=self.initial_sampling_rate,
            output="sos",
        )
        self.emg_data = signal.sosfiltfilt(sos, filtered_data, axis=0)
        return self.emg_data

    def downsample_emg(self) -> NDArray[np.float64]:
        self._ensure_emg_data()
        self._ensure_initial_sampling_rate()

        greatest_common_divisor = np.gcd(
            self.initial_sampling_rate,
            self.required_sampling_rate,
        )
        up = self.required_sampling_rate // greatest_common_divisor
        down = self.initial_sampling_rate // greatest_common_divisor

        self.emg_data = signal.resample_poly(self.emg_data, up=up, down=down, axis=0)
        return self.emg_data

    def create_timestamps(self) -> NDArray[np.float64]:
        self._ensure_emg_data()

        samples_count = self.emg_data.shape[0]
        self.timestamps = (
            np.arange(samples_count, dtype=np.float64)
            * 1000
            / self.required_sampling_rate
        )
        return self.timestamps

    def save_new_data(self) -> Path:
        self._ensure_emg_data()
        self._ensure_timestamps()

        output_path = Path("tmp") / "emg.hdf5"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with h5py.File(output_path, "w") as hdf_file:
            hdf_file.create_dataset("emg", data=self.emg_data)
            hdf_file.create_dataset("timestamps", data=self.timestamps)

        return output_path

    def _read_selected_channels(self, emg_dataset: h5py.Dataset) -> NDArray[Any]:
        if emg_dataset.ndim == 3:
            selected_data = emg_dataset[:, :, self.channels_slice]
            return selected_data.reshape(-1, selected_data.shape[-1])

        if emg_dataset.ndim == 2:
            return emg_dataset[:, self.channels_slice]

        raise ValueError("EMG dataset must be a 2D or 3D array.")

    @staticmethod
    def _extract_initial_sampling_rate(
        hdf_file: h5py.File,
        emg_group: h5py.Group,
        emg_dataset: h5py.Dataset,
    ) -> int:
        if "sampling_rate" in emg_group.attrs:
            return int(emg_group.attrs["sampling_rate"])

        if "sampling_rate" in hdf_file.attrs:
            return int(hdf_file.attrs["sampling_rate"])

        if emg_dataset.ndim == 3:
            return int(emg_dataset.shape[1])

        raise ValueError(
            "initial_sampling_rate could not be detected from HDF5 attributes."
        )

    def _ensure_emg_data(self):
        if self.emg_data is None:
            raise ValueError("EMG data is empty. Run extract_emg_data first.")

    def _ensure_timestamps(self):
        if self.timestamps is None:
            raise ValueError("Timestamps are empty. Run create_timestamps first.")

    def _ensure_initial_sampling_rate(self):
        if self.initial_sampling_rate is None:
            raise ValueError(
                "Initial sampling rate is empty. Run extract_emg_data first."
            )
