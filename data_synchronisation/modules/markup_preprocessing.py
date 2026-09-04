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

        with h5py.File(self.file_dir, "r") as hdf_file:
            self.exercises: NDArray[np.int8] = np.asarray(
                hdf_file["markup"]["exercises"][:],
                dtype=np.int8,
            )

    def __call__(self):
        self.exercises = self.clean_markup(self.exercises)
        self.exercises = self.remove_zeros(self.exercises)
        self.repeats = self.create_repeats(self.exercises)

    @staticmethod
    def clean_markup(markup: NDArray) -> NDArray:
        new_markup = list()
        last_seen = None
        for exercise in markup:
            if exercise != last_seen:
                new_markup.append(exercise)

            last_seen = exercise

        return np.array(new_markup, dtype=np.int8)

    @staticmethod
    def remove_zeros(markup: NDArray) -> NDArray:
        return markup[markup != 0]

    @staticmethod
    def create_repeats(markup: NDArray) -> NDArray:
        counter = dict()
        repeats = np.zeros_like(markup, dtype=np.int8)

        for idx, exercise in enumerate(markup):
            if not exercise in counter:
                counter[exercise] = 1
            
            repeats[idx] = counter[exercise]
            counter[exercise] += 1

        return repeats
