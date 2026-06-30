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
        self._ensure_lia_data()
        self.lia_data = self.butter_lowpass_filter(
            self.lia_data,
            fs=self.sampling_rate,
            cutoff=lowpass_cutoff,
            order=4
        )

        if normalize:
            self.lia_data = self.zscore(self.lia_data)


    @staticmethod
    def normalized_corr(x: np.ndarray, y: np.ndarray) -> float:
        """
        Нормализованная корреляция двух фрагментов.
        NaN-значения игнорируются.
        """
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        mask = np.isfinite(x) & np.isfinite(y)

        if np.sum(mask) < 5:
            return -np.inf

        x = x[mask]
        y = y[mask]

        x = x - np.mean(x)
        y = y - np.mean(y)

        denom = np.sqrt(np.sum(x ** 2) * np.sum(y ** 2)) + 1e-12

        return np.sum(x * y) / denom


    @staticmethod
    def shift_1d_signal(x: np.ndarray, lag_samples: int) -> np.ndarray:
        """
        Сдвигает сигнал внутри окна.

        Конвенция:
        lag_samples > 0:
            сигнал x запаздывает относительно опорного сигнала,
            поэтому его нужно сдвинуть влево.

        lag_samples < 0:
            сигнал x опережает опорный сигнал,
            поэтому его нужно сдвинуть вправо.

        Пустые области заполняются NaN.
        """
        x = np.asarray(x, dtype=float)
        y = np.full_like(x, np.nan, dtype=float)

        if lag_samples == 0:
            y[:] = x

        elif lag_samples > 0:
            y[:-lag_samples] = x[lag_samples:]

        else:
            lag = abs(lag_samples)
            y[lag:] = x[:-lag]

        return y


    def estimate_window_lag(
        self,
        acc_window: np.ndarray,
        emg_window: np.ndarray,
        max_lag_samples: int
    ) -> tuple[int, float]:
        """
        Ищет локальный сдвиг ЭМГ относительно ускорения.

        Возвращает:
            best_lag_samples, best_corr
        """
        best_lag = 0
        best_score = -np.inf

        for lag in range(-max_lag_samples, max_lag_samples + 1):
            emg_shifted = self.shift_1d_signal(emg_window, lag)
            score = self.normalized_corr(acc_window, emg_shifted)

            if score > best_score:
                best_score = score
                best_lag = lag

        return best_lag, best_score


    def align_signals_by_local_lags(
        self,
        window_sec: float = 10.0,
        step_sec: float = 1.0,
        max_lag_sec: float = 2.0,
        smooth_lags: bool = True,
        min_corr: float | None = None
    ):
        """
        Оконная синхронизация ЭМГ и линейного ускорения.

        Parameters
        ----------
        window_sec : float
            Длина окна в секундах.
        step_sec : float
            Шаг окна в секундах.
        max_lag_sec : float
            Максимальный допустимый локальный сдвиг в секундах.
        smooth_lags : bool
            Сглаживать ли последовательность найденных сдвигов.
        min_corr : float | None
            Минимальная допустимая корреляция окна.
            Если None, используются все окна.
        """

        if len(self.emg_data) != len(self.lia_data):
            # raise ValueError("emg_signal и acc_signal должны иметь одинаковую длину")
            min_len = min(len(self.emg_data), len(self.lia_data))
            self.emg_data = self.emg_data[:min_len]
            self.lia_data = self.lia_data[:min_len]

        n = len(self.emg_data)

        window_size = int(round(window_sec * self.sampling_rate))
        step_size = int(round(step_sec * self.sampling_rate))
        max_lag_samples = int(round(max_lag_sec * self.sampling_rate))

        if window_size <= 2 * max_lag_samples:
            raise ValueError(
                "window_sec должен быть существенно больше max_lag_sec. "
                "Например: window_sec=10, max_lag_sec=2."
            )

        if step_size < 1:
            raise ValueError("step_sec слишком мал для данной fs")

        # Накопители для overlap-add
        emg_accumulator = np.zeros(n, dtype=float)
        acc_accumulator = np.zeros(n, dtype=float)
        weight_accumulator = np.zeros(n, dtype=float)

        # Весовое окно для плавной склейки
        weight_window = windows.hann(window_size, sym=False)

        # Чтобы края окна не имели нулевой вес
        weight_window = weight_window + 1e-6

        window_starts = list(range(0, n - window_size + 1, step_size))

        # Чтобы последний участок тоже попал в обработку
        if window_starts[-1] != n - window_size:
            window_starts.append(n - window_size)

        raw_lags = []
        corr_scores = []
        centers = []

        # Сначала оцениваем лаги для всех окон
        for start in window_starts:
            end = start + window_size

            acc_window = self.lia_data[start:end]
            emg_window = self.emg_data[start:end]

            lag, score = self.estimate_window_lag(
                acc_window=acc_window,
                emg_window=emg_window,
                max_lag_samples=max_lag_samples
            )

            raw_lags.append(lag)
            corr_scores.append(score)
            centers.append((start + end) / 2 / self.sampling_rate)

        raw_lags = np.asarray(raw_lags, dtype=int)
        corr_scores = np.asarray(corr_scores, dtype=float)
        centers = np.asarray(centers, dtype=float)

        # При необходимости отбрасываем окна с плохой корреляцией
        lags_for_use = raw_lags.astype(float)

        if min_corr is not None:
            bad = corr_scores < min_corr

            if np.any(bad):
                good = ~bad

                if np.sum(good) >= 2:
                    lags_for_use[bad] = np.interp(
                        centers[bad],
                        centers[good],
                        lags_for_use[good]
                    )
                else:
                    lags_for_use[bad] = 0

        # Сглаживание сдвигов, чтобы убрать скачки от ложных корреляций
        if smooth_lags and len(lags_for_use) >= 5:
            lags_for_use = median_filter(lags_for_use, size=5)

        lags_for_use = np.round(lags_for_use).astype(int)

        # Теперь сдвигаем окна и собираем итоговый сигнал
        for start, lag in zip(window_starts, lags_for_use):
            end = start + window_size

            acc_window = self.lia_data[start:end]
            emg_window = self.emg_data[start:end]

            emg_shifted = self.shift_1d_signal(emg_window, lag)

            valid = np.isfinite(emg_shifted) & np.isfinite(acc_window)

            local_weight = weight_window.copy()
            local_weight[~valid] = 0.0

            emg_accumulator[start:end] += np.nan_to_num(emg_shifted) * local_weight
            acc_accumulator[start:end] += np.nan_to_num(acc_window) * local_weight
            weight_accumulator[start:end] += local_weight

        valid_total = weight_accumulator > 0

        emg_aligned = np.full(n, np.nan, dtype=float)
        acc_aligned = np.full(n, np.nan, dtype=float)

        emg_aligned[valid_total] = (
            emg_accumulator[valid_total] / weight_accumulator[valid_total]
        )

        acc_aligned[valid_total] = (
            acc_accumulator[valid_total] / weight_accumulator[valid_total]
        )

        self.emg_data = emg_aligned
        self.lia_data = acc_aligned
    

    def _ensure_emg_data(self):
        if self.emg_data is None:
            raise ValueError("EMG data is empty. Run extract_emg first.")

    def _ensure_emg_timestamps(self):
        if self.emg_timestamps is None:
            raise ValueError("EMG timestamps are empty. Run extract_emg first.")

    def _ensure_lia_data(self):
        if self.lia_data is None:
            raise ValueError("LIA data is empty. Run extract_lia first.")
