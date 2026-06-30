from pathlib import Path

import h5py
import numpy as np
from numpy.typing import NDArray


class MarkupDataPreprocessing:
    def __init__(
        self,
        file_dir: str | Path,
    ):
        self.file_dir = Path(file_dir)

        self.timestamps: NDArray[np.float64] | None = None
        self.exercises: NDArray[np.int8] | None = None

    def extract_timestamps(self):
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.timestamps = np.asarray(
                hdf_file["markup"]["timestamps"][:],
                dtype=np.float64,
            )

    def extract_markup(self):
        with h5py.File(self.file_dir, "r") as hdf_file:
            self.exercises = np.asarray(
                hdf_file["markup"]["exercises"][:],
                dtype=np.int8,
            )

    def clean_markup(self):
        self._ensure_timestamps()
        self._ensure_exercises()

        _, unique_indices = np.unique(self.timestamps, return_index=True)
        mask = np.zeros(self.timestamps.shape, dtype=bool)
        mask[np.sort(unique_indices)] = True

        self.timestamps = self.timestamps[mask]
        self.exercises = self.exercises[mask]

    def save_markup(self):
        self._ensure_timestamps()
        self._ensure_exercises()

        output_path = Path("tmp") / "markup.hdf5"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with h5py.File(output_path, "w") as hdf_file:
            hdf_file.create_dataset("timestamps", data=self.timestamps)
            hdf_file.create_dataset("exercises", data=self.exercises)

    def _ensure_timestamps(self):
        if self.timestamps is None:
            raise ValueError("Timestamps are empty. Run extract_timestamps first.")

    def _ensure_exercises(self):
        if self.exercises is None:
            raise ValueError("Exercises are empty. Run extract_markup first.")
