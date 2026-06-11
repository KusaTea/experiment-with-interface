from pathlib import Path
import sys

import numpy as np

try:
    from data_observing.experiment_data_reader import ExperimentDataReader
except ModuleNotFoundError:
    from experiment_data_reader import ExperimentDataReader


class RecordDataVerification:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.reader = ExperimentDataReader(self.file_path)

    def close(self):
        self.reader.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def verify_participant_data(self):
        participant_info = self.reader.get_participant_info()

        title = "INFORMATION ABOUT A PARTICIPANT"
        self._print_title(title)
        print(f"- code: {participant_info.get('participant_code')}")
        print(f"- age: {participant_info.get('participant_age')}")
        print(f"- gender: {participant_info.get('participant_gender')}")
        print(f"- leading hand: {participant_info.get('participant_leading_hand')}")

    def record_length(self):
        _, emg_data = self.reader.get_emg_data()
        duration_in_seconds = int(emg_data.shape[0])

        title = "RECORD LENGTH"
        self._print_title(title)
        print(self._format_seconds(duration_in_seconds))

    def glove_average_fps(self):
        timestamps = self._get_glove_timestamps_in_seconds()

        if timestamps.size < 2:
            average_glove_fps = 0
        else:
            duration = timestamps[-1] - timestamps[0]
            average_glove_fps = (timestamps.size - 1) / duration if duration > 0 else 0

        title = "GLOVE AVERAGE FPS"
        self._print_title(title)
        print(average_glove_fps)

    def plot_glove_data_delta_histogram(self):
        import matplotlib.pyplot as plt

        timestamps = self._get_glove_timestamps_in_seconds()
        deltas = np.diff(timestamps)

        participant_code = self.reader.get_participant_info().get("participant_code")
        save_dir = Path("../verification_data") / str(participant_code)
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / "glove_data_delta.png"

        plt.figure(figsize=(10, 6))
        if deltas.size:
            bins = np.arange(0, np.ceil(deltas.max()) + 1, 1)
            if bins.size < 2:
                bins = np.array([0, 1])
            plt.hist(deltas, bins=bins)
        plt.xlabel("Delta, s")
        plt.ylabel("Count")
        plt.title("Glove Data Delta Histogram")
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    def emg_n_channels(self):
        _, emg_data = self.reader.get_emg_data()
        number_of_channels = emg_data.shape[-1]

        title = "NUMBER OF EMG CHANNELS"
        self._print_title(title)
        print(number_of_channels)

    def plot_emg_data(self):
        _, emg_data = self.reader.get_emg_data()
        participant_code = self.reader.get_participant_info().get("participant_code")
        save_dir = Path("../verification_data") / str(participant_code) / "emg_data"
        save_dir.mkdir(parents=True, exist_ok=True)

        selected_channels = emg_data[:, :, 64:192]
        calibration_data = self._flatten_emg_interval(selected_channels, 0, 30)
        self._plot_channels_grid(calibration_data, save_dir / "calibration.png", first_channel_number=65)

        for picture_idx, start_second in enumerate(self._random_starts(emg_data.shape[0], 30, 6), start=1):
            interval_data = self._flatten_emg_interval(selected_channels, start_second, 30)
            self._plot_channels_grid(interval_data, save_dir / f"{picture_idx}.png", first_channel_number=65)

    def plot_imu_data(self):
        timestamps, imu_data = self.reader.get_imu_data()
        participant_code = self.reader.get_participant_info().get("participant_code")
        save_dir = Path("../verification_data") / str(participant_code) / "imu_data"
        save_dir.mkdir(parents=True, exist_ok=True)

        timestamps = self._normalize_timestamps_for_data(timestamps, imu_data)

        calibration_data = self._slice_data_by_seconds(timestamps, imu_data, 0, 30)
        self._plot_channels_grid(calibration_data, save_dir / "calibration.png")

        max_duration = int(timestamps[-1] - timestamps[0]) if timestamps.size else 0
        for picture_idx, start_second in enumerate(self._random_starts(max_duration, 60, 6), start=1):
            interval_data = self._slice_data_by_seconds(timestamps, imu_data, start_second, 60)
            self._plot_channels_grid(interval_data, save_dir / f"{picture_idx}.png")

    @staticmethod
    def _print_title(title: str):
        print("=" * len(title))
        print(title)

    @staticmethod
    def _format_seconds(seconds: int) -> str:
        hours = seconds // 3600
        minutes = seconds % 3600 // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def _get_glove_timestamps_in_seconds(self):
        timestamps, _ = self.reader.get_hand_quaternions()
        timestamps = np.asarray(timestamps, dtype=np.float64)

        if timestamps.size < 2:
            return timestamps

        # SensoGlove timestamps are stored in milliseconds in the raw reader.
        return timestamps / 1000

    @staticmethod
    def _flatten_emg_interval(emg_data, start_second: int, duration_in_seconds: int):
        interval = emg_data[start_second:start_second + duration_in_seconds]
        if interval.size == 0:
            return np.empty((0, emg_data.shape[-1]))
        return interval.reshape(-1, interval.shape[-1])

    @staticmethod
    def _random_starts(record_duration: int, interval_duration: int, number_of_intervals: int):
        max_start = max(record_duration - interval_duration, 0)
        if max_start == 0:
            return [0] * number_of_intervals

        rng = np.random.default_rng()
        return [int(value) for value in rng.integers(0, max_start + 1, size=number_of_intervals)]

    @staticmethod
    def _plot_channels_grid(data, save_path: Path, first_channel_number: int = 1):
        import matplotlib.pyplot as plt

        data = np.asarray(data)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        elif data.ndim > 2:
            data = data.reshape(data.shape[0], -1)

        fig, axes = plt.subplots(13, 10, figsize=(26, 20), sharex=True)
        axes = axes.ravel()

        number_of_channels = data.shape[1] if data.size else 0
        for channel_idx, ax in enumerate(axes):
            if channel_idx < number_of_channels:
                ax.plot(data[:, channel_idx], linewidth=0.5)
                ax.set_title(str(first_channel_number + channel_idx), fontsize=8)
            ax.tick_params(labelsize=6)

        fig.tight_layout()
        fig.savefig(save_path)
        plt.close(fig)

    @staticmethod
    def _normalize_timestamps_for_data(timestamps, data):
        timestamps = np.asarray(timestamps, dtype=np.float64)
        data = np.asarray(data)

        if timestamps.size != data.shape[0]:
            return np.arange(data.shape[0], dtype=np.float64)

        if timestamps.size < 2:
            return timestamps

        timestamps = timestamps / 1000
        return timestamps - timestamps[0]

    @staticmethod
    def _slice_data_by_seconds(timestamps, data, start_second: int, duration_in_seconds: int):
        if timestamps.size == 0:
            return data[:0]

        start = timestamps[0] + start_second
        end = start + duration_in_seconds
        mask = (timestamps >= start) & (timestamps < end)
        return data[mask]


if __name__=='__main__':
    if len(sys.argv) > 2:
        raise ValueError('The function requires 1 argument: file directory')

    file_dir = Path(sys.argv[1])
    record_data_verificator = RecordDataVerification(file_dir)
    record_data_verificator.verify_participant_data()
    record_data_verificator.record_length()
    record_data_verificator.glove_average_fps()
    record_data_verificator.plot_glove_data_delta_histogram()
    record_data_verificator.emg_n_channels()
    record_data_verificator.plot_emg_data()
    record_data_verificator.plot_imu_data()
