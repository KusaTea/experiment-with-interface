from pathlib import Path
from sys import sys

from verify_record_data import RecordDataVerification


if __name__=='__main__':
    if len(sys.argv) > 2:
        raise ValueError('The function requires 1 argument: file directory')

    file_dir = Path(sys.argv[1])
    record_data_verificator = RecordDataVerification(file_dir)
    record_data_verificator.verify_participant_data()
    record_data_verificator.record_length()
    record_data_verificator.glove_average_fps()
    record_data_verificator.emg_n_channels()