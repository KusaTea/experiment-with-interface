from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import h5py
import numpy as np
from numpy.typing import NDArray


AlignmentMethod = Literal["auto", "timestamps", "signals", "activity", "none"]
TimestampUnit = Literal["auto", "s", "ms"]
ChunkTimestampPosition = Literal["start", "center", "end"]


@dataclass(frozen=True)
class SynchronizationConfig:
    emg_sampling_rate_hz: float = 10240.0
    timestamp_unit: TimestampUnit = "auto"
    emg_chunk_timestamp_position: ChunkTimestampPosition = "end"
    glove_method: AlignmentMethod = "auto"
    markup_method: AlignmentMethod = "auto"
    feature_rate_hz: float = 100.0
    max_signal_lag_ms: float | None = None


@dataclass(frozen=True)
class SynchronizationResult:
    output_path: Path
    emg_samples: int
    glove_samples: int
    markup_events: int
    glove_offset_ms: float
    markup_offset_ms: float
    glove_method: str
    markup_method: str


def synchronize_record(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    overwrite: bool = False,
    config: SynchronizationConfig | None = None,
) -> SynchronizationResult:
    """Create a new experiment HDF5 file with synchronized data only.

    The source file is not modified. The output file keeps the original HDF5
    layout (`emg`, `position`, `markup` groups), but all timestamps are
    rewritten to the zero-based EMG master time scale.
    """
    input_path = Path(input_path)
    config = config or SynchronizationConfig()

    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_synchronized{input_path.suffix}")
    output_path = Path(output_path)
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Output path must differ from input path")

    if output_path.exists():
        if not overwrite:
            raise FileExistsError(f"Output file already exists: {output_path}")
        output_path.unlink()

    with h5py.File(input_path, "r") as source, h5py.File(output_path, "w") as target:
        emg = source["emg"]["emg"]
        emg_shape = emg.shape
        emg_samples = _count_emg_samples(emg_shape)
        emg_time_ms = make_emg_time_ms(emg_samples, config.emg_sampling_rate_hz)

        emg_abs_start_ms = _estimate_emg_absolute_start_ms(
            source["emg"]["timestamps"][:],
            emg_shape,
            config,
        )

        glove_time_ms, _, glove_offset_ms, glove_method = _align_glove(
            source,
            emg_time_ms,
            emg_abs_start_ms,
            config,
        )

        markup_time_ms, markup_offset_ms, markup_method = _align_markup(
            source,
            emg_time_ms,
            emg_abs_start_ms,
            config,
        )

        _write_synchronized_file(
            source=source,
            target=target,
            emg_time_ms=emg_time_ms,
            glove_time_ms=glove_time_ms,
            markup_time_ms=markup_time_ms,
        )

        return SynchronizationResult(
            output_path=output_path,
            emg_samples=emg_samples,
            glove_samples=int(glove_time_ms.size),
            markup_events=int(markup_time_ms.size),
            glove_offset_ms=float(glove_offset_ms),
            markup_offset_ms=float(markup_offset_ms),
            glove_method=glove_method,
            markup_method=markup_method,
        )


def make_emg_time_ms(number_of_samples: int, sampling_rate_hz: float = 10240.0) -> NDArray[np.float64]:
    """Return a zero-based EMG master time scale in milliseconds."""
    if number_of_samples < 0:
        raise ValueError("number_of_samples must be non-negative")
    return np.arange(number_of_samples, dtype=np.float64) * (1000.0 / sampling_rate_hz)


def flatten_emg(emg: NDArray) -> NDArray:
    """Convert EMG data from (chunks, samples, channels) to (samples, channels)."""
    emg = np.asarray(emg)
    if emg.ndim == 2:
        return emg
    if emg.ndim != 3:
        raise ValueError(f"Expected 2D or 3D EMG data, got shape {emg.shape}")
    return emg.reshape(-1, emg.shape[-1])


def _align_glove(
    hdf: h5py.File,
    emg_time_ms: NDArray[np.float64],
    emg_abs_start_ms: float | None,
    config: SynchronizationConfig,
) -> tuple[NDArray[np.float64], NDArray[np.float64] | None, float, str]:
    timestamps = np.asarray(hdf["position"]["timestamps"][:], dtype=np.float64)
    if timestamps.size == 0:
        return timestamps, None, 0.0, "none"

    relative_ms = _relative_time_ms(timestamps, config.timestamp_unit)
    method = _resolve_glove_method(hdf, timestamps, emg_abs_start_ms, config)
    imu_data = np.asarray(hdf["position"]["imu"][:], dtype=np.float64)
    imu_relative_ms = _time_for_data(relative_ms, imu_data.shape[0])

    if method == "timestamps":
        absolute_ms = _source_absolute_ms(
            timestamps,
            config.timestamp_unit,
            start_timestamp=hdf["position"].attrs.get("start_timestamp"),
        )
        aligned_ms = absolute_ms - emg_abs_start_ms
        offset_ms = float(aligned_ms[0] - relative_ms[0])
        imu_time_ms = imu_relative_ms + offset_ms if imu_relative_ms.size != aligned_ms.size else None
        return aligned_ms, imu_time_ms, offset_ms, method

    if method == "signals":
        emg_data = flatten_emg(hdf["emg"]["emg"][:])
        offset_ms = estimate_signal_offset_ms(
            reference_time_ms=emg_time_ms,
            reference_feature=_emg_activity_feature(emg_data, config.emg_sampling_rate_hz),
            source_time_ms=imu_relative_ms,
            source_feature=_movement_feature(imu_data),
            feature_rate_hz=config.feature_rate_hz,
            max_lag_ms=config.max_signal_lag_ms,
        )
        imu_time_ms = imu_relative_ms + offset_ms if imu_relative_ms.size != relative_ms.size else None
        return relative_ms + offset_ms, imu_time_ms, float(offset_ms), method

    imu_time_ms = imu_relative_ms if imu_relative_ms.size != relative_ms.size else None
    return relative_ms, imu_time_ms, 0.0, "none"


def _align_markup(
    hdf: h5py.File,
    emg_time_ms: NDArray[np.float64],
    emg_abs_start_ms: float | None,
    config: SynchronizationConfig,
) -> tuple[NDArray[np.float64], float, str]:
    timestamps = np.asarray(hdf["markup"]["timestamps"][:], dtype=np.float64)
    if timestamps.size == 0:
        return timestamps, 0.0, "none"

    relative_ms = _relative_time_ms(timestamps, config.timestamp_unit)
    method = _resolve_markup_method(timestamps, emg_abs_start_ms, config)

    if method == "timestamps":
        absolute_ms = _timestamps_to_ms(timestamps, config.timestamp_unit)
        aligned_ms = absolute_ms - emg_abs_start_ms
        return aligned_ms, float(aligned_ms[0] - relative_ms[0]), method

    if method == "activity":
        emg_data = flatten_emg(hdf["emg"]["emg"][:])
        exercises = np.asarray(hdf["markup"]["exercises"][:])
        offset_ms = estimate_signal_offset_ms(
            reference_time_ms=emg_time_ms,
            reference_feature=_emg_activity_feature(emg_data, config.emg_sampling_rate_hz),
            source_time_ms=relative_ms,
            source_feature=_markup_activity_feature(relative_ms, exercises),
            feature_rate_hz=config.feature_rate_hz,
            max_lag_ms=config.max_signal_lag_ms,
        )
        return relative_ms + offset_ms, float(offset_ms), method

    return relative_ms, 0.0, "none"


def estimate_signal_offset_ms(
    reference_time_ms: NDArray[np.float64],
    reference_feature: NDArray[np.float64],
    source_time_ms: NDArray[np.float64],
    source_feature: NDArray[np.float64],
    *,
    feature_rate_hz: float = 100.0,
    max_lag_ms: float | None = None,
) -> float:
    """Estimate offset that must be added to source_time_ms to match reference."""
    if reference_time_ms.size < 2 or source_time_ms.size < 2:
        return 0.0

    step_ms = 1000.0 / feature_rate_hz
    ref_grid, ref_values = _resample_to_uniform_grid(reference_time_ms, reference_feature, step_ms)
    src_grid, src_values = _resample_to_uniform_grid(source_time_ms, source_feature, step_ms)
    if ref_values.size < 2 or src_values.size < 2:
        return 0.0

    ref_values = _standardize(ref_values)
    src_values = _standardize(src_values)

    correlation = np.correlate(ref_values, src_values, mode="full")
    lags = np.arange(-src_values.size + 1, ref_values.size, dtype=np.float64)

    if max_lag_ms is not None:
        max_lag_samples = int(round(max_lag_ms / step_ms))
        mask = np.abs(lags) <= max_lag_samples
        if np.any(mask):
            correlation = correlation[mask]
            lags = lags[mask]

    best_lag_samples = lags[int(np.argmax(correlation))]
    return float((ref_grid[0] - src_grid[0]) + best_lag_samples * step_ms)


def _resolve_glove_method(
    hdf: h5py.File,
    timestamps: NDArray[np.float64],
    emg_abs_start_ms: float | None,
    config: SynchronizationConfig,
) -> Literal["timestamps", "signals", "none"]:
    if config.glove_method in ("timestamps", "signals", "none"):
        return config.glove_method
    if emg_abs_start_ms is not None and _can_make_absolute(timestamps, hdf["position"].attrs.get("start_timestamp")):
        return "timestamps"
    return "signals"


def _resolve_markup_method(
    timestamps: NDArray[np.float64],
    emg_abs_start_ms: float | None,
    config: SynchronizationConfig,
) -> Literal["timestamps", "activity", "none"]:
    if config.markup_method == "signals":
        return "activity"
    if config.markup_method in ("timestamps", "activity", "none"):
        return config.markup_method
    if emg_abs_start_ms is not None and _looks_like_epoch_ms(_timestamps_to_ms(timestamps, config.timestamp_unit)):
        return "timestamps"
    return "activity"


def _estimate_emg_absolute_start_ms(
    emg_timestamps: NDArray,
    emg_shape: tuple[int, ...],
    config: SynchronizationConfig,
) -> float | None:
    emg_timestamps = np.asarray(emg_timestamps, dtype=np.float64)
    if emg_timestamps.size == 0:
        return None

    emg_ts_ms = _timestamps_to_ms(emg_timestamps, config.timestamp_unit)
    if not _looks_like_epoch_ms(emg_ts_ms):
        return None

    if len(emg_shape) == 3:
        chunk_duration_ms = emg_shape[1] * 1000.0 / config.emg_sampling_rate_hz
    else:
        chunk_duration_ms = 0.0

    if config.emg_chunk_timestamp_position == "start":
        return float(emg_ts_ms[0])
    if config.emg_chunk_timestamp_position == "center":
        return float(emg_ts_ms[0] - chunk_duration_ms / 2.0)
    return float(emg_ts_ms[0] - chunk_duration_ms)


def _source_absolute_ms(
    timestamps: NDArray[np.float64],
    timestamp_unit: TimestampUnit,
    *,
    start_timestamp,
) -> NDArray[np.float64]:
    timestamp_ms = _timestamps_to_ms(timestamps, timestamp_unit)
    if _looks_like_epoch_ms(timestamp_ms):
        return timestamp_ms

    if start_timestamp is None:
        raise ValueError("Cannot build absolute source timestamps without start_timestamp")

    start_ms = _timestamps_to_ms(np.asarray([float(start_timestamp)]), timestamp_unit)[0]
    if _looks_like_epoch_ms(start_ms):
        if timestamp_ms[0] > 10 * 60 * 1000:
            return start_ms + (timestamp_ms - timestamp_ms[0])
        return start_ms + timestamp_ms

    raise ValueError("start_timestamp does not look like an absolute timestamp")


def _can_make_absolute(timestamps: NDArray[np.float64], start_timestamp) -> bool:
    timestamp_ms = _timestamps_to_ms(timestamps, "auto")
    if _looks_like_epoch_ms(timestamp_ms):
        return True
    if start_timestamp is None:
        return False
    start_ms = _timestamps_to_ms(np.asarray([float(start_timestamp)]), "auto")[0]
    return bool(_looks_like_epoch_ms(start_ms))


def _timestamps_to_ms(timestamps: NDArray, unit: TimestampUnit) -> NDArray[np.float64]:
    timestamps = np.asarray(timestamps, dtype=np.float64)
    if unit == "ms":
        return timestamps
    if unit == "s":
        return timestamps * 1000.0

    if timestamps.size == 0:
        return timestamps

    finite = timestamps[np.isfinite(timestamps)]
    if finite.size == 0:
        return timestamps

    positive_deltas = np.diff(np.sort(finite))
    positive_deltas = positive_deltas[positive_deltas > 0]
    median_delta = float(np.median(positive_deltas)) if positive_deltas.size else 0.0
    max_abs_value = float(np.max(np.abs(finite)))

    if max_abs_value > 1e11:
        return timestamps
    if max_abs_value > 1e8:
        return timestamps * 1000.0
    if median_delta > 10.0:
        return timestamps
    return timestamps * 1000.0


def _relative_time_ms(timestamps: NDArray, unit: TimestampUnit) -> NDArray[np.float64]:
    timestamp_ms = _timestamps_to_ms(timestamps, unit)
    if timestamp_ms.size == 0:
        return timestamp_ms
    return timestamp_ms - timestamp_ms[0]


def _time_for_data(reference_time_ms: NDArray[np.float64], number_of_rows: int) -> NDArray[np.float64]:
    if number_of_rows <= 0:
        return np.empty(0, dtype=np.float64)
    if reference_time_ms.size == number_of_rows:
        return reference_time_ms
    if reference_time_ms.size < 2:
        return np.arange(number_of_rows, dtype=np.float64)
    return np.linspace(reference_time_ms[0], reference_time_ms[-1], number_of_rows, dtype=np.float64)


def _looks_like_epoch_ms(timestamps_ms: NDArray | float) -> bool:
    values = np.asarray(timestamps_ms, dtype=np.float64)
    if values.size == 0:
        return False
    return bool(np.nanmax(np.abs(values)) > 1e11)


def _count_emg_samples(emg_shape: tuple[int, ...]) -> int:
    if len(emg_shape) == 2:
        return int(emg_shape[0])
    if len(emg_shape) == 3:
        return int(emg_shape[0] * emg_shape[1])
    raise ValueError(f"Expected 2D or 3D EMG shape, got {emg_shape}")


def _write_flattened_emg(sync_group: h5py.Group, emg_dataset: h5py.Dataset) -> None:
    if len(emg_dataset.shape) == 2:
        sync_group.create_dataset("emg", data=emg_dataset[:])
        return

    if len(emg_dataset.shape) != 3:
        raise ValueError(f"Expected 2D or 3D EMG dataset, got {emg_dataset.shape}")

    chunks, samples_per_chunk, channels = emg_dataset.shape
    flat = sync_group.create_dataset(
        "emg",
        shape=(chunks * samples_per_chunk, channels),
        dtype=emg_dataset.dtype,
        chunks=(min(samples_per_chunk, chunks * samples_per_chunk), channels),
    )
    for chunk_idx in range(chunks):
        start = chunk_idx * samples_per_chunk
        end = start + samples_per_chunk
        flat[start:end, :] = emg_dataset[chunk_idx, :, :]


def _write_synchronized_file(
    *,
    source: h5py.File,
    target: h5py.File,
    emg_time_ms: NDArray[np.float64],
    glove_time_ms: NDArray[np.float64],
    markup_time_ms: NDArray[np.float64],
) -> None:
    _copy_attrs(source, target)

    emg_group = target.create_group("emg")
    _copy_attrs(source["emg"], emg_group)
    emg_group.create_dataset("timestamps", data=emg_time_ms)
    _write_flattened_emg(emg_group, source["emg"]["emg"])

    position_group = target.create_group("position")
    _copy_attrs(source["position"], position_group)
    if "start_timestamp" in position_group.attrs:
        position_group.attrs["start_timestamp"] = glove_time_ms[0] if glove_time_ms.size else 0.0
    position_group.create_dataset("imu", data=source["position"]["imu"][:])
    position_group.create_dataset("bones", data=source["position"]["bones"][:])
    position_group.create_dataset("fingers", data=source["position"]["fingers"][:])
    position_group.create_dataset("timestamps", data=glove_time_ms)

    markup_group = target.create_group("markup")
    _copy_attrs(source["markup"], markup_group)
    markup_group.create_dataset("timestamps", data=markup_time_ms)
    markup_group.create_dataset("exercises", data=source["markup"]["exercises"][:])


def _copy_attrs(source, target) -> None:
    for key, value in source.attrs.items():
        target.attrs[key] = value


def _emg_activity_feature(emg_data: NDArray, sampling_rate_hz: float) -> NDArray[np.float64]:
    emg_data = np.asarray(emg_data, dtype=np.float64)
    if emg_data.ndim == 1:
        emg_data = emg_data.reshape(-1, 1)
    window = max(1, int(round(0.05 * sampling_rate_hz)))
    squared = np.mean(emg_data * emg_data, axis=1)
    kernel = np.ones(window, dtype=np.float64) / window
    return np.sqrt(np.convolve(squared, kernel, mode="same"))


def _movement_feature(data: NDArray) -> NDArray[np.float64]:
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    else:
        data = data.reshape(data.shape[0], -1)

    if data.shape[0] < 2:
        return np.zeros(data.shape[0], dtype=np.float64)

    derivative = np.diff(data, axis=0, prepend=data[[0], :])
    return np.linalg.norm(derivative, axis=1)


def _markup_activity_feature(time_ms: NDArray[np.float64], exercises: NDArray) -> NDArray[np.float64]:
    if time_ms.size == 0:
        return np.empty(0, dtype=np.float64)
    return (np.asarray(exercises) != 0).astype(np.float64)


def _resample_to_uniform_grid(
    time_ms: NDArray[np.float64],
    values: NDArray[np.float64],
    step_ms: float,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    time_ms = np.asarray(time_ms, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    if time_ms.size == 0 or values.size == 0:
        return np.empty(0, dtype=np.float64), np.empty(0, dtype=np.float64)

    size = min(time_ms.size, values.size)
    time_ms = time_ms[:size]
    values = values[:size]

    order = np.argsort(time_ms)
    time_ms = time_ms[order]
    values = values[order]

    unique_time, unique_idx = np.unique(time_ms, return_index=True)
    values = values[unique_idx]
    if unique_time.size < 2:
        return unique_time, values

    grid = np.arange(unique_time[0], unique_time[-1] + step_ms, step_ms, dtype=np.float64)
    return grid, np.interp(grid, unique_time, values)


def _standardize(values: NDArray[np.float64]) -> NDArray[np.float64]:
    values = np.asarray(values, dtype=np.float64)
    values = values - np.mean(values)
    std = np.std(values)
    if std == 0:
        return values
    return values / std


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronize an experiment HDF5 file offline.")
    parser.add_argument("input", type=Path, help="Input HDF5 file.")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output HDF5 file.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output file if it exists.")
    parser.add_argument("--sampling-rate", type=float, default=10240.0, help="EMG sampling rate in Hz.")
    parser.add_argument(
        "--emg-chunk-timestamp-position",
        choices=("start", "center", "end"),
        default="end",
        help="Where each stored EMG chunk timestamp is located inside the chunk.",
    )
    parser.add_argument(
        "--glove-method",
        choices=("auto", "timestamps", "signals", "none"),
        default="auto",
        help="Glove alignment method.",
    )
    parser.add_argument(
        "--markup-method",
        choices=("auto", "timestamps", "activity", "none"),
        default="auto",
        help="Markup alignment method.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    result = synchronize_record(
        args.input,
        args.output,
        overwrite=args.overwrite,
        config=SynchronizationConfig(
            emg_sampling_rate_hz=args.sampling_rate,
            emg_chunk_timestamp_position=args.emg_chunk_timestamp_position,
            glove_method=args.glove_method,
            markup_method=args.markup_method,
        ),
    )
    print(f"Saved: {result.output_path}")
    print(f"EMG samples: {result.emg_samples}")
    print(f"Glove samples: {result.glove_samples}, offset ms: {result.glove_offset_ms:.3f}, method: {result.glove_method}")
    print(f"Markup events: {result.markup_events}, offset ms: {result.markup_offset_ms:.3f}, method: {result.markup_method}")


if __name__ == "__main__":
    main()
