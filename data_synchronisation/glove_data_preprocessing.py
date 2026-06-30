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

        self.timestamps: NDArray[np.float64] | None = None
        self.lia_data: NDArray[np.float32] | None = None
        self.fingers_quaternions: NDArray[np.float32] | None = None
        self.bones_quaternions: NDArray[np.float32] | None = None

    def __call__(self):
        self.extract_timestamps()
        self.extract_lia_data()
        self.transform_lia_data()
        self.interpolate_lia()
        self.save_lia_data()
        
        self.extract_fingers_data()
        self.interpolate_fingers()
        self.save_fingers_data()

        self.extract_bones_data()
        self.interpolate_bones()
        self.save_bones_data()

    def extract_timestamps(self):
        with h5py.File(self.file_dir, "r") as hdf_file:
            timestamps = hdf_file["position"]["timestamps"][:] / 1_000 # transform from ms to s
            timestamps = np.asarray(
                timestamps,
                dtype=np.float64,
            )

        self.timestamps = timestamps - np.min(timestamps)

    def extract_lia_data(self):
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.lia_data = np.asarray(
                hdf_file["position"]["lia"][:],
                dtype=np.float32,
            )

    def transform_lia_data(self):
        self._ensure_lia_data()

        self.lia_data = np.max(np.sqrt((self.lia_data ** 2).sum(axis=1)), axis=-1).astype(np.float32)

    def interpolate_lia(self):
        self._ensure_timestamps()
        self._ensure_lia_data()

        interpolation_timestamps = self._create_interpolation_timestamps()
        self.lia_data = np.interp(
            interpolation_timestamps,
            self.timestamps,
            self.lia_data,
        ).astype(np.float32)

    def save_lia_data(self):
        self._ensure_lia_data()

        self._save_dataset("lia", self.lia_data)
        self.lia_data = None

    def extract_fingers_data(self):
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.fingers_quaternions = np.asarray(
                hdf_file["position"]["fingers"][:],
                dtype=np.float32,
            )

    def interpolate_fingers(self):
        self._ensure_timestamps()
        self._ensure_fingers_quaternions()

        self.fingers_quaternions = self._interpolate_quaternions(
            self.fingers_quaternions
        )

    def save_fingers_data(self):
        self._ensure_fingers_quaternions()

        self._save_dataset("fingers", self.fingers_quaternions)
        self.fingers_quaternions = None

    def extract_bones_data(self):
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.bones_quaternions = np.asarray(
                hdf_file["position"]["bones"][:],
                dtype=np.float32,
            )

    def interpolate_bones(self):
        self._ensure_timestamps()
        self._ensure_bones_quaternions()

        self.bones_quaternions = self._interpolate_quaternions(
            self.bones_quaternions
        )

    def save_bones_data(self):
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

    def _create_interpolation_timestamps(self) -> NDArray[np.float64]:
        self._ensure_timestamps()

        step = 1 / self.required_sampling_rate
        samples_count = (
            int(np.floor(np.max(self.timestamps) * self.required_sampling_rate)) + 1
        )
        return (np.arange(samples_count, dtype=np.float64) * step).astype(np.float64)

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

    def _ensure_lia_data(self):
        if self.lia_data is None:
            raise ValueError(
                "Accelerometers data is empty. Run extract_lia_data first."
            )

    def _ensure_fingers_quaternions(self):
        if self.fingers_quaternions is None:
            raise ValueError("Fingers data is empty. Run extract_fingers_data first.")

    def _ensure_bones_quaternions(self):
        if self.bones_quaternions is None:
            raise ValueError("Bones data is empty. Run extract_bones_data first.")
