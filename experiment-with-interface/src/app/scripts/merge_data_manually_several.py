from merge_data_manually import merge_data_manually
from pathlib import Path


if __name__=='__main__':
    ready_dir = Path('/home/matthew/datasets/EMG_glove/')
    raw_dir = ready_dir / 'raw'
    for participant_code in range(1, 8):
        merge_data_manually(
            raw_data_dir=raw_dir / f'{participant_code}',
            ready_data_dir=ready_dir / f'{participant_code}.hdf5',
            ans='y'
        )