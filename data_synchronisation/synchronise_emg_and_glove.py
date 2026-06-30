from pathlib import Path

import h5py
import numpy as np
from numpy.typing import NDArray
from scipy import signal


class SynchroniseEMGAndGlove:
    def __init__(
        self,
        emg_dir: str | Path,
        glove_dir: str | Path,
    ):
        self.emg_dir = Path(emg_dir)
        self.glove_dir = Path(glove_dir)

        self.emg_data: NDArray[np.float64] | None = None
        self.emg_timestamps: NDArray[np.float64] | None = None
        self.lia_data: NDArray[np.float64] | None = None
        self.time_gap: float | None = None

    def extract_emg(self):
        with h5py.File(self.emg_dir, "r") as hdf_file:
            self.emg_data = np.asarray(hdf_file["emg"][:], dtype=np.float64)
            self.emg_timestamps = np.asarray(
                hdf_file["timestamps"][:],
                dtype=np.float64,
            )

    def transform_emg(self):
        self._ensure_emg_data()

        self.emg_data = np.abs(self.emg_data)
        if self.emg_data.ndim == 1:
            return

        self.emg_data = np.max(self.emg_data, axis=-1)

    def extract_lia(self):
        with h5py.File(self.glove_dir, "r") as hdf_file:
            self.lia_data = np.asarray(hdf_file["lia"][:], dtype=np.float64)

    def get_time_gap(self) -> float:
        self._ensure_emg_data()
        self._ensure_emg_timestamps()
        self._ensure_lia_data()

        emg_signal = self._normalize_signal(self.emg_data)
        lia_signal = self._normalize_signal(self.lia_data)

        correlation = signal.correlate(lia_signal, emg_signal, mode="full")
        lags = signal.correlation_lags(
            lia_signal.shape[0],
            emg_signal.shape[0],
            mode="full",
        )

        lag_samples = int(lags[np.argmax(correlation)])
        self.time_gap = lag_samples * self._get_emg_sampling_period()
        return self.time_gap

    @staticmethod
    def _normalize_signal(data: NDArray[np.float64]) -> NDArray[np.float64]:
        data = np.asarray(data, dtype=np.float64).reshape(-1)
        std = np.std(data)

        if std == 0:
            raise ValueError("Cannot calculate cross-correlation for a constant signal.")

        return (data - np.mean(data)) / std

    def _get_emg_sampling_period(self) -> float:
        if self.emg_timestamps.shape[0] < 2:
            raise ValueError("At least two EMG timestamps are required.")

        return float(np.median(np.diff(self.emg_timestamps)))

    def _ensure_emg_data(self):
        if self.emg_data is None:
            raise ValueError("EMG data is empty. Run extract_emg first.")

    def _ensure_emg_timestamps(self):
        if self.emg_timestamps is None:
            raise ValueError("EMG timestamps are empty. Run extract_emg first.")

    def _ensure_lia_data(self):
        if self.lia_data is None:
            raise ValueError("LIA data is empty. Run extract_lia first.")
