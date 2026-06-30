from pathlib import Path

import h5py
import numpy as np
from numpy.typing import NDArray


class GloveDataPreprocessing:
    def __init__(
        self,
        file_dir: str | Path,
        required_sampling_rate: int,
    ):
        self.file_dir = Path(file_dir)
        self.required_sampling_rate = required_sampling_rate

        self.timestamps: NDArray[np.float32] | None = None
        self.accelerometers_data: NDArray[np.float32] | None = None
        self.fingers_quaternions: NDArray[np.float32] | None = None
        self.bones_quaternions: NDArray[np.float32] | None = None

    def extract_timestamps(self) -> NDArray[np.float32]:
        with h5py.File(self.file_dir, "r") as hdf_file:
            timestamps = np.asarray(
                hdf_file["position"]["timestamps"] / 1_000_000, # transform from microseconds to seconds
                dtype=np.float32,
            )

        self.timestamps = timestamps - np.min(timestamps)

    def extract_accelerometers_data(self) -> NDArray[np.float32]:
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.accelerometers_data = np.asarray(
                hdf_file["position"]["imu"][:, :, 5:8],
                dtype=np.float32,
            )

    def transform_accelerometers_data(self) -> NDArray[np.float32]:
        self._ensure_accelerometers_data()

        self.accelerometers_data = np.max(
            np.abs(self.accelerometers_data),
            axis=(1, 2),
        ).astype(np.float32)

    def interpolate_accelerometers(self) -> NDArray[np.float32]:
        self._ensure_timestamps()
        self._ensure_accelerometers_data()

        interpolation_timestamps = self._create_interpolation_timestamps()
        self.accelerometers_data = np.interp(
            interpolation_timestamps,
            self.timestamps,
            self.accelerometers_data,
        ).astype(np.float32)

    def save_accelerometers_data(self) -> Path:
        self._ensure_accelerometers_data()

        self._save_dataset("imu", self.accelerometers_data)
        self.accelerometers_data = None

    def extract_fingers_data(self) -> NDArray[np.float32]:
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.fingers_quaternions = np.asarray(
                hdf_file["position"]["fingers"],
                dtype=np.float32,
            )

    def interpolate_fingers(self) -> NDArray[np.float32]:
        self._ensure_timestamps()
        self._ensure_fingers_quaternions()

        self.fingers_quaternions = self._interpolate_quaternions(
            self.fingers_quaternions
        )

    def save_fingers_data(self) -> Path:
        self._ensure_fingers_quaternions()

        self._save_dataset("fingers", self.fingers_quaternions)
        self.fingers_quaternions = None

    def extract_bones_data(self) -> NDArray[np.float32]:
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.bones_quaternions = np.asarray(
                hdf_file["position"]["bones"],
                dtype=np.float32,
            )

    def interpolate_bones(self) -> NDArray[np.float32]:
        self._ensure_timestamps()
        self._ensure_bones_quaternions()

        self.bones_quaternions = self._interpolate_quaternions(
            self.bones_quaternions
        )

    def save_bones_data(self) -> Path:
        self._ensure_bones_quaternions()

        output_path = self._save_dataset("bones", self.bones_quaternions)
        self.bones_quaternions = None

    def _interpolate_quaternions(
        self,
        quaternions: NDArray[np.float32],
    ) -> NDArray[np.float32]:
        interpolation_timestamps = self._create_interpolation_timestamps()
        interpolated_quaternions = np.empty(
            (
                interpolation_timestamps.shape[0],
                quaternions.shape[1],
                quaternions.shape[2],
            ),
            dtype=np.float32,
        )

        for item_idx in range(quaternions.shape[1]):
            for value_idx in range(quaternions.shape[2]):
                interpolated_quaternions[:, item_idx, value_idx] = np.interp(
                    interpolation_timestamps,
                    self.timestamps,
                    quaternions[:, item_idx, value_idx],
                )

        return interpolated_quaternions

    def _create_interpolation_timestamps(self) -> NDArray[np.float32]:
        self._ensure_timestamps()

        step = 1 / self.required_sampling_rate
        samples_count = (
            int(np.floor(np.max(self.timestamps) * self.required_sampling_rate)) + 1
        )
        return (np.arange(samples_count, dtype=np.float32) * step).astype(np.float32)

    @staticmethod
    def _save_dataset(
        key: str,
        data: NDArray[np.float32],
    ) -> Path:
        output_path = Path("tmp") / "glove.hdf5"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with h5py.File(output_path, "a") as hdf_file:
            if key in hdf_file:
                del hdf_file[key]
            hdf_file.create_dataset(key, data=data)

        return output_path

    def _ensure_timestamps(self):
        if self.timestamps is None:
            raise ValueError("Timestamps are empty. Run extract_timestamps first.")

    def _ensure_accelerometers_data(self):
        if self.accelerometers_data is None:
            raise ValueError(
                "Accelerometers data is empty. Run extract_accelerometers_data first."
            )

    def _ensure_fingers_quaternions(self):
        if self.fingers_quaternions is None:
            raise ValueError("Fingers data is empty. Run extract_fingers_data first.")

    def _ensure_bones_quaternions(self):
        if self.bones_quaternions is None:
            raise ValueError("Bones data is empty. Run extract_bones_data first.")
