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
        emg_reader = self.reader.get_emg_data()
        duration_in_seconds = int(emg_reader.shape[0])

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
            counts, bin_edges, patches = plt.hist(deltas, bins=bins)
            for count, patch in zip(counts, patches):
                if count == 0:
                    continue
                x = patch.get_x() + patch.get_width() / 2
                y = patch.get_height()
                plt.text(x, y, str(int(count)), ha="center", va="bottom", fontsize=9)
        plt.xlabel("Delta, s")
        plt.ylabel("Count")
        plt.title("Glove Data Delta Histogram")
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    def emg_n_channels(self):
        emg_reader = self.reader.get_emg_data()
        number_of_channels = emg_reader.shape[-1]

        title = "NUMBER OF EMG CHANNELS"
        self._print_title(title)
        print(number_of_channels)

    def plot_emg_data(self):
        emg_reader = self.reader.get_emg_data()
        participant_code = self.reader.get_participant_info().get("participant_code")
        save_dir = Path("../verification_data") / str(participant_code) / "emg_data"
        save_dir.mkdir(parents=True, exist_ok=True)

        _, calibration_interval = emg_reader[0:30]
        calibration_data = self._flatten_emg_interval(calibration_interval)
        self._plot_emg_interval_figures(calibration_data, save_dir, "calibration")

        for picture_idx, start_second in enumerate(self._random_starts(emg_reader.shape[0], 30, 6), start=1):
            _, interval = emg_reader[start_second:start_second + 30]
            interval_data = self._flatten_emg_interval(interval)
            self._plot_emg_interval_figures(interval_data, save_dir, str(picture_idx))

    def plot_imu_data(self):
        imu_reader = self.reader.get_imu_data()
        participant_code = self.reader.get_participant_info().get("participant_code")
        save_dir = Path("../verification_data") / str(participant_code) / "imu_data"
        save_dir.mkdir(parents=True, exist_ok=True)

        timestamps = self._get_reader_timestamps_in_seconds(imu_reader)

        calibration_data = self._slice_reader_by_seconds(imu_reader, timestamps, 0, 30)
        self._plot_imu_grid(calibration_data, save_dir / "calibration.png")

        max_duration = int(timestamps[-1] - timestamps[0]) if timestamps.size else 0
        for picture_idx, start_second in enumerate(self._random_starts(max_duration, 60, 6), start=1):
            interval_data = self._slice_reader_by_seconds(imu_reader, timestamps, start_second, 60)
            self._plot_imu_grid(interval_data, save_dir / f"{picture_idx}.png")

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
        return self._get_reader_timestamps_in_seconds(self.reader.get_hand_quaternions())

    @staticmethod
    def _get_reader_timestamps_in_seconds(data_reader):
        timestamps = np.asarray(data_reader.timestamps[:], dtype=np.float64)

        if timestamps.size < 2:
            return timestamps

        # SensoGlove timestamps are stored in milliseconds in the raw reader.
        timestamps = timestamps / 1000
        return timestamps - timestamps[0]

    @staticmethod
    def _flatten_emg_interval(interval):
        if interval.size == 0:
            return np.empty((0, interval.shape[-1] if interval.ndim else 0))
        return interval.reshape(-1, interval.shape[-1])

    @staticmethod
    def _random_starts(record_duration: int, interval_duration: int, number_of_intervals: int):
        max_start = max(record_duration - interval_duration, 0)
        if max_start == 0:
            return [0] * number_of_intervals

        rng = np.random.default_rng()
        return [int(value) for value in rng.integers(0, max_start + 1, size=number_of_intervals)]

    def _plot_emg_interval_figures(self, data, save_dir: Path, picture_prefix: str):
        number_of_channels = data.shape[-1] if data.ndim >= 2 else 0
        if number_of_channels == 0:
            self._plot_channels_grid(data, save_dir / f"{picture_prefix}_last_24.png", rows=4, columns=6)
            return

        last_channels_start = max(number_of_channels - 24, 0)
        last_channels = data[:, last_channels_start:number_of_channels]
        self._plot_channels_grid(
            last_channels,
            save_dir / f"{picture_prefix}_last_24.png",
            first_channel_number=last_channels_start + 1,
            rows=4,
            columns=6,
        )

        remaining_channels_end = last_channels_start
        figure_idx = 1
        while remaining_channels_end > 0:
            channels_start = max(remaining_channels_end - 64, 0)
            channels = data[:, channels_start:remaining_channels_end]
            self._plot_channels_grid(
                channels,
                save_dir / f"{picture_prefix}_{figure_idx}.png",
                first_channel_number=channels_start + 1,
                rows=8,
                columns=8,
            )
            remaining_channels_end = channels_start
            figure_idx += 1

    @staticmethod
    def _plot_channels_grid(
        data,
        save_path: Path,
        first_channel_number: int = 1,
        rows: int = 13,
        columns: int = 10,
    ):
        import matplotlib.pyplot as plt

        data = np.asarray(data)
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        elif data.ndim > 2:
            data = data.reshape(data.shape[0], -1)

        fig, axes = plt.subplots(rows, columns, figsize=(columns * 3, rows * 2.5), sharex=True)
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
    def _plot_imu_grid(data, save_path: Path):
        import matplotlib.pyplot as plt

        data = np.asarray(data)
        if data.ndim == 2 and data.shape[1] == 72:
            data = data.reshape(data.shape[0], 9, 8)

        fig, axes = plt.subplots(9, 8, figsize=(24, 22.5), sharex=True)

        for sensor_idx in range(9):
            for channel_idx in range(8):
                ax = axes[sensor_idx, channel_idx]
                if data.ndim == 3 and data.shape[1] > sensor_idx and data.shape[2] > channel_idx:
                    ax.plot(data[:, sensor_idx, channel_idx], linewidth=0.5)
                ax.set_title(f"{sensor_idx + 1}_{channel_idx + 1}", fontsize=8)
                ax.tick_params(labelsize=6)

        fig.tight_layout()
        fig.savefig(save_path)
        plt.close(fig)

    @staticmethod
    def _slice_reader_by_seconds(data_reader, timestamps, start_second: int, duration_in_seconds: int):
        if timestamps.size == 0:
            return data_reader.values[:0]

        start = timestamps[0] + start_second
        end = start + duration_in_seconds
        start_idx = int(np.searchsorted(timestamps, start, side="left"))
        end_idx = int(np.searchsorted(timestamps, end, side="left"))
        _, data = data_reader[start_idx:end_idx]
        return data


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
