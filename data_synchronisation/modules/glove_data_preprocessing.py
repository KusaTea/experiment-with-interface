from pathlib import Path

import h5py
import numpy as np
from numpy.typing import NDArray
from scipy import interpolate, signal


class GloveDataPreprocessing:
    def __init__(
        self,
        file_dir: str | Path,
        required_sampling_rate: int,
    ):
        self.file_dir = Path(file_dir)
        self.required_sampling_rate = required_sampling_rate

        self.timestamps: NDArray[np.float64] | None = None
        self.lia_data: NDArray[np.float32] | None = None
        self.lia_norm: NDArray[np.float32] | None = None

    def __call__(self):
        self.extract_timestamps()
        self.extract_lia_data()
        self.interpolate_lia_data()
        self.calculate_lia_norm()
        self.filter_lia_norm()
        self.normalise_lia_norm()

    def extract_timestamps(self):
        with h5py.File(self.file_dir, "r") as hdf_file:
            timestamps = hdf_file["position"]["timestamps"][:] / 1_000 # transform from ms to s
            timestamps = np.asarray(
                timestamps,
                dtype=np.float64,
            )

        self.timestamps = timestamps - timestamps[0]

    def extract_lia_data(self):
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.lia_data = np.asarray(
                hdf_file["position"]["lia"][:],
                dtype=np.float32,
            )

    def interpolate_lia_data(self):
        self._ensure_timestamps()
        self._ensure_lia_data()

        interpolation_timestamps = self._create_interpolation_timestamps()

        interpolater = interpolate.interp1d(
            x=self.timestamps,
            y=self.lia_data,
            axis=0
        )
        self.lia_data = interpolater(interpolation_timestamps)

    def calculate_lia_norm(self):
        self.lia_norm = np.sqrt((self.lia_data ** 2).sum(axis=-1)).astype(np.float32)

    def filter_lia_norm(self):
        sos = signal.butter(
            N=4,
            Wn=5,
            btype="lowpass",
            fs=1024,
            output="sos"
        )
        self.lia_norm = signal.sosfiltfilt(sos, self.lia_norm, axis=0)

    def normalise_lia_norm(self):
        self.lia_norm = (self.lia_norm - np.median(self.lia_norm, axis=0)) / self.lia_norm.std(axis=0)
    
    def _create_interpolation_timestamps(self) -> NDArray[np.float64]:
        self._ensure_timestamps()

        step = 1 / self.required_sampling_rate
        samples_count = (
            int(np.floor(np.max(self.timestamps) * self.required_sampling_rate)) + 1
        )
        return (np.arange(samples_count, dtype=np.float64) * step).astype(np.float64)


    def _ensure_timestamps(self):
        if self.timestamps is None:
            raise ValueError("Timestamps are empty. Run extract_timestamps first.")

    def _ensure_lia_data(self):
        if self.lia_data is None:
            raise ValueError(
                "Accelerometers data is empty. Run extract_lia_data first."
            )
