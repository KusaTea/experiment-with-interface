from pathlib import Path

import h5py
import numpy as np
from numpy.typing import NDArray
from scipy import signal
from scipy.signal import butter, filtfilt


class SynchroniseEMGAndGlove:
    def __init__(
        self,
        emg_dir: str | Path,
        glove_dir: str | Path,
        sampling_rate: int
    ):
        self.emg_dir = Path(emg_dir)
        self.glove_dir = Path(glove_dir)

        self.emg_data: NDArray[np.float64] | None = None
        self.emg_timestamps: NDArray[np.float64] | None = None
        self.lia_data: NDArray[np.float64] | None = None
        self.time_gap: float | None = None
        self.sampling_rate = sampling_rate

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

    @staticmethod
    def zscore(x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        return (x - np.nanmean(x)) / (np.nanstd(x) + 1e-12)

    @staticmethod
    def butter_lowpass_filter(
        x: np.ndarray,
        fs: float,
        cutoff: float = 5.0,
        order: int = 4
    ) -> np.ndarray:
        x = np.asarray(x, dtype=float)

        nyquist = fs / 2
        normalized_cutoff = cutoff / nyquist

        b, a = butter(order, normalized_cutoff, btype="low")
        return filtfilt(b, a, x)

    @staticmethod
    def moving_rms(
        x: np.ndarray,
        fs: float,
        window_ms: float = 100.0
    ) -> np.ndarray:
        x = np.asarray(x, dtype=float)

        window_size = int(fs * window_ms / 1000)

        if window_size < 1:
            window_size = 1

        kernel = np.ones(window_size) / window_size

        x_squared = x ** 2
        x_rms = np.sqrt(np.convolve(x_squared, kernel, mode="same"))

        return x_rms


    def smooth_emg(
        self,
        rms_window_ms: float = 100.0,
        lowpass_cutoff: float = 5.0,
        normalize: bool = True
    ) -> np.ndarray:

        # RMS-огибающая
        self.emg_data = self.moving_rms(
            self.emg_data,
            fs=self.sampling_rate,
            window_ms=rms_window_ms
        )

        # Дополнительное сглаживание огибающей
        self.emg_data = self.butter_lowpass_filter(
            self.emg_data,
            fs=self.sampling_rate,
            cutoff=lowpass_cutoff,
            order=4
        )

        if normalize:
            self.emg_data = self.zscore(self.emg_data)


    def smooth_linear_acceleration(
        self,
        lowpass_cutoff: float = 5.0,
        normalize: bool = True
    ) -> np.ndarray:
        self.lia_data = self.butter_lowpass_filter(
            self.lia_data,
            fs=self.sampling_rate,
            cutoff=lowpass_cutoff,
            order=4
        )

        if normalize:
            self.lia_data = self.zscore(self.lia_data)
    
    
    def get_time_gap(self) -> float:
        self._ensure_emg_data()
        self._ensure_emg_timestamps()
        self._ensure_lia_data()

        correlation = signal.correlate(self.lia_signal, self.emg_signal, mode="full")
        lags = signal.correlation_lags(
            self.lia_signal.shape[0],
            self.emg_signal.shape[0],
            mode="full",
        )

        lag_samples = int(lags[np.argmax(correlation)])
        self.time_gap = lag_samples * self._get_emg_sampling_period()
        return self.time_gap

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
