from pathlib import Path

import h5py
import numpy as np
from numpy.typing import NDArray
from scipy.signal import butter, filtfilt, windows
from scipy.ndimage import median_filter


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

        self.synced_emg_idx: NDArray | None = None
        self.synced_glove_idx: NDArray | None = None

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
        self._ensure_emg_data()

        self.emg_data = self.moving_rms(
            self.emg_data,
            fs=self.sampling_rate,
            window_ms=rms_window_ms
        )

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
        self._ensure_lia_data()
        self.lia_data = self.butter_lowpass_filter(
            self.lia_data,
            fs=self.sampling_rate,
            cutoff=lowpass_cutoff,
            order=4
        )

        if normalize:
            self.lia_data = self.zscore(self.lia_data)


    import numpy as np

    @staticmethod
    def normalized_corr(x: np.ndarray, y: np.ndarray, min_points: int = 5) -> float:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        mask = np.isfinite(x) & np.isfinite(y)

        if np.sum(mask) < min_points:
            return -np.inf

        x = x[mask]
        y = y[mask]

        x = x - np.mean(x)
        y = y - np.mean(y)

        denom = np.sqrt(np.sum(x ** 2) * np.sum(y ** 2))

        if denom < 1e-12:
            return -np.inf

        return float(np.sum(x * y) / denom)

    @staticmethod
    def get_overlap_for_lag(
        n: int,
        lag: int
    ) -> tuple[np.ndarray, np.ndarray]:

        if abs(lag) >= n:
            return np.array([], dtype=int), np.array([], dtype=int)

        if lag > 0:
            idx_a = np.arange(0, n - lag)
            idx_b = np.arange(lag, n)

        elif lag < 0:
            shift = -lag
            idx_a = np.arange(shift, n)
            idx_b = np.arange(0, n - shift)

        else:
            idx_a = np.arange(0, n)
            idx_b = np.arange(0, n)

        return idx_a, idx_b

    def estimate_lag_for_window(
        self,
        signal_a_window: np.ndarray,
        signal_b_window: np.ndarray,
        max_lag_samples: int,
        min_points: int = 5
    ) -> tuple[int, float]:

        signal_a_window = np.asarray(signal_a_window, dtype=float)
        signal_b_window = np.asarray(signal_b_window, dtype=float)

        if len(signal_a_window) != len(signal_b_window):
            raise ValueError("Окна должны иметь одинаковую длину.")

        n = len(signal_a_window)

        best_lag = 0
        best_corr = -np.inf

        for lag in range(-max_lag_samples, max_lag_samples + 1):
            idx_a, idx_b = self.get_overlap_for_lag(n, lag)

            if len(idx_a) < min_points:
                continue

            x = signal_a_window[idx_a]
            y = signal_b_window[idx_b]

            corr = self.normalized_corr(x, y, min_points=min_points)

            if corr > best_corr:
                best_corr = corr
                best_lag = lag

        return best_lag, best_corr


    def build_sync_indices_by_nonoverlap_windows(
        self,
        window_size: int,
        max_lag_samples: int,
        min_corr: float | None = None,
        drop_last_incomplete: bool = True,
        min_points: int = 5
    ) -> dict:

        if self.emg_data.ndim != 1:
            raise ValueError("signal_a должен быть одномерным массивом.")

        if self.lia_data.ndim != 1:
            raise ValueError("signal_b должен быть одномерным массивом.")

        if len(self.emg_data) != len(self.lia_data):
            # raise ValueError(
            #     "signal_a и signal_b должны иметь одинаковую длину."
            # )
            self.min_len = min(len(self.emg_data), len(self.lia_data))
            self.emg_data = self.emg_data[:self.min_len]
            self.lia_data = self.lia_data[:self.min_len]

        if window_size <= 1:
            raise ValueError("window_size должен быть больше 1.")

        if max_lag_samples < 0:
            raise ValueError("max_lag_samples должен быть >= 0.")

        if max_lag_samples >= window_size:
            raise ValueError(
                "max_lag_samples должен быть меньше window_size."
            )

        n_samples = len(self.emg_data)

        window_starts = []
        window_ends = []

        start = 0

        while start < n_samples:
            end = start + window_size

            if end > n_samples:
                if drop_last_incomplete:
                    break
                else:
                    end = n_samples

            if end - start > max_lag_samples + min_points:
                window_starts.append(start)
                window_ends.append(end)

            start += window_size

        window_starts = np.asarray(window_starts, dtype=int)
        window_ends = np.asarray(window_ends, dtype=int)

        idx_emg_all = []
        idx_lia_all = []

        lags = []
        corr_scores = []
        used_windows_mask = []

        for start, end in zip(window_starts, window_ends):
            emg_window = self.emg_data[start:end]
            lia_window = self.lia_data[start:end]

            current_window_size = end - start

            lag, corr = self.estimate_lag_for_window(
                signal_a_window=emg_window,
                signal_b_window=lia_window,
                max_lag_samples=min(max_lag_samples, current_window_size - 1),
                min_points=min_points
            )

            lags.append(lag)
            corr_scores.append(corr)

            if min_corr is not None and corr < min_corr:
                used_windows_mask.append(False)
                continue

            idx_emg_local, idx_lia_local = self.get_overlap_for_lag(
                n=current_window_size,
                lag=lag
            )

            if len(idx_emg_local) < min_points:
                used_windows_mask.append(False)
                continue

            idx_emg_global = start + idx_emg_local
            idx_lia_global = start + idx_lia_local

            idx_emg_all.append(idx_emg_global)
            idx_lia_all.append(idx_lia_global)

            used_windows_mask.append(True)

        if len(idx_emg_all) == 0:
            self.synced_emg_idx = np.array([], dtype=int)
            self.synced_glove_idx = np.array([], dtype=int)
        else:
            self.synced_emg_idx = np.concatenate(idx_emg_all)
            self.synced_glove_idx = np.concatenate(idx_lia_all)

        lags = np.asarray(lags, dtype=int)
        corr_scores = np.asarray(corr_scores, dtype=float)
        used_windows_mask = np.asarray(used_windows_mask, dtype=bool)
    
    def sync_emg_signal(self, emg_signal: NDArray) -> NDArray:
        return emg_signal[self.synced_emg_idx]

    def sync_glove_signal(self, glove_signal: NDArray) -> NDArray:
        return glove_signal[self.synced_glove_idx]
    

    def _ensure_emg_data(self):
        if self.emg_data is None:
            raise ValueError("EMG data is empty. Run extract_emg first.")

    def _ensure_emg_timestamps(self):
        if self.emg_timestamps is None:
            raise ValueError("EMG timestamps are empty. Run extract_emg first.")

    def _ensure_lia_data(self):
        if self.lia_data is None:
            raise ValueError("LIA data is empty. Run extract_lia first.")
    
    def _ensure_sync_idx(self):
        if self.synced_emg_idx is None or self.synced_glove_idx:
            raise ValueError("There are no sync indeces. Run build_sync_indices_by_nonoverlap_windows first.")
