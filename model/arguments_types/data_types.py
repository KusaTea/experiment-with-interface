from typing import TypedDict

from numpy.typing import NDArray


class EMGDataType(TypedDict):
    emg: NDArray
    timestamps: NDArray


class SensoGloveDataType(TypedDict):
    start: int
    imu: NDArray
    bones: NDArray
    fingers: NDArray
    timestamps: NDArray


class MarkupDataType(TypedDict):
    timestamps: NDArray
    exercises: NDArray