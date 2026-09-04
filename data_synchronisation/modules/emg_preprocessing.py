from pathlib import Path
import h5py

import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import rfft, rfftfreq

DPI = plt.rcParams['figure.dpi']

class EMGPreprocessing:
    def __init__(
        self,
        file_dir: str | Path,
        channels_slice: slice,
    ):
        self.file_dir = Path(file_dir)

        self.initial_sampling_rate: int | None = None
        
        with h5py.File(self.file_dir, mode='r') as hdf_file:
            emg_group = hdf_file.get('emg')
            mV_constant = float(emg_group.attrs.get('mV_constant'))
            self.emg_data: NDArray[np.float32] = np.asarray(emg_group.get('emg')[:, :, channels_slice], dtype=np.float32) * mV_constant
            self.initial_sampling_rate = self.emg_data.shape[1]
            self.emg_data = self.emg_data.reshape(-1, 128)

        print('data is extracted'.upper())
        print(self.emg_data.dtype)
        print(self.emg_data.shape)

    def __call__(
        self,
        high_threshold: float = 10,
        low_threshold: float = 500,
        required_sampling_rate: int = 1024
    ):
        tmp_folder = Path('./tmp/plots/') / self.file_dir.name.split('.')[0]
        tmp_folder.mkdir(parents=True, exist_ok=True)
        self.emg_data = self.remove_dc(self.emg_data)
        self.plot_fft(self.emg_data[:, 0], self.initial_sampling_rate, save_dir=tmp_folder / 'after_dc_remove.png')

        for channel_idx in range(self.emg_data.shape[1]):
            self.emg_data[:, channel_idx] = self.filter_signal(
                self.emg_data[:, channel_idx],
                sampling_rate=self.initial_sampling_rate,
                high_threshold=high_threshold,
                low_threshold=low_threshold
            )
        self.plot_fft(self.emg_data[:, 0], self.initial_sampling_rate, save_dir=tmp_folder / 'after_filters.png')

        for channel_idx in range(self.emg_data.shape[1]):
            self.emg_data[:, channel_idx] = self.remove_selected_harmonics(
                self.emg_data[:, channel_idx],
                sampling_rate=self.initial_sampling_rate,
                freqs_to_remove=[50, 100, 200, 300, 400]
            )
        self.plot_fft(self.emg_data[:, 0], self.initial_sampling_rate, save_dir=tmp_folder / 'after_notch.png')
        
        self.emg_data = self.downsample_signal(
            self.emg_data,
            cur_sampling_rate=self.initial_sampling_rate,
            required_sampling_rate=required_sampling_rate
        )
        self.plot_signal(self.emg_data[:, 0], save_dir=tmp_folder / 'after_downsampling.png')
    

    @staticmethod
    def plot_signal(signal_data: NDArray, save_dir: None | str = None):
        plt.close()
        fig, ax = plt.subplots(ncols=1, nrows=1)
        fig.set_size_inches(w=1500 / DPI, h=500 / DPI)
    
        ax.plot(signal_data)
        
        plt.tight_layout()
        if save_dir:
            plt.savefig(save_dir)
        else:
            plt.show()
    

    def plot_fft(self, signal_data: NDArray, sampling_rate: int, save_dir: None | str = None):
        amps, freqs = self.apply_fft(signal_data, sampling_rate)
        
        idx, = np.where(freqs < 500)
        amps = amps[idx]
        freqs = freqs[idx]
        
        plt.close()
        fig, axes = plt.subplots(ncols=1, nrows=2)
        fig.set_size_inches(w=1500 / DPI, h=500 / DPI)
        
        axes[0].plot(freqs, amps)
        axes[0].set_xlabel('Frequency, Hz')
        axes[0].set_ylabel('Amplitude, mV')
    
        axes[1].plot(signal_data)
        
        plt.tight_layout()
        if save_dir:
            plt.savefig(save_dir)
        else:
            plt.show()
    

    @staticmethod
    def apply_fft(signal_data: NDArray, sampling_rate: int) -> tuple[NDArray, NDArray]:
        amps = np.abs(rfft(signal_data))
        freqs = rfftfreq(len(signal_data), d=1 / sampling_rate)
    
        return amps, freqs
    

    @staticmethod
    def remove_dc(signal_data: NDArray, remover_type: str = 'mean'):
        if remover_type == 'mean':
            return signal_data - signal_data.mean(axis=0)
    
        else:
            return signal_data - signal_data.median(axis=0)
    

    @staticmethod
    def filter_signal(signal_data: NDArray, sampling_rate: int, high_threshold: float | None = None, low_threshold: float | None = None) -> NDArray:
        assert high_threshold or low_threshold, "At least one threshold must be provided"
    
        if high_threshold is None or low_threshold is None:
            if high_threshold is None:
                low_pass = low_threshold / (sampling_rate / 2)
                b, a = signal.butter(4, low_pass, btype='lowpass')
        
            elif low_threshold is None:
                high_pass = high_threshold / (sampling_rate / 2)
                b, a = signal.butter(4, high_pass, btype='highpass')
    
            return signal.filtfilt(b, a, signal_data, axis=0)
    
        else:
            low_pass = low_threshold / (sampling_rate / 2)
            high_pass = high_threshold / (sampling_rate / 2)
            sos = signal.butter(4, [high_pass, low_pass], btype='bandpass', output='sos')
            return signal.sosfiltfilt(sos, signal_data, axis=0)
    

    @staticmethod
    def notch_filter(signal_data, sampling_rate, freq, q=30):
        b, a = signal.iirnotch(w0=freq, Q=q, fs=sampling_rate)
        return signal.filtfilt(b, a, signal_data, axis=0)
    

    def remove_selected_harmonics(self, signal_data, sampling_rate, freqs_to_remove, q=30):
        signal_copy = signal_data.copy()
    
        for f0 in freqs_to_remove:
            if f0 < sampling_rate / 2:
                signal_copy = self.notch_filter(signal_copy, sampling_rate, freq=f0, q=q)
    
        return signal_copy
    

    @staticmethod
    def downsample_signal(signal_data: NDArray, cur_sampling_rate: int, required_sampling_rate: int) -> NDArray[np.float32]:
            greatest_common_divisor = np.gcd(
                cur_sampling_rate,
                required_sampling_rate,
            )
            up = required_sampling_rate // greatest_common_divisor
            down = cur_sampling_rate // greatest_common_divisor
    
            samples = int(signal_data.shape[0] / cur_sampling_rate * required_sampling_rate)
    
            downsampled_data = np.empty((samples, signal_data.shape[-1]), dtype=np.float32)
            downsampled_data = signal.resample_poly(signal_data, up=up, down=down, axis=0)
            return downsampled_data
    

    @staticmethod
    def rectify_signal(signal_data):
        return np.abs(signal_data)
