import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path


class BasicSettingsCreater:

    basic_settings = {
        'lang': 'eng',
        'save_directory': './data',
        'myograph_settings': {
            'ip': '169.254.1.10',
            'port': 23456,
            'options': {
                'acquisition_byte_info': {
                    'decimator': False,
                    'start_record_with_trigger': False,
                    'sampling_rate': 10240,
                    'channels_for_analog_output': 2,
                    'data_transfer_to_pc': True,
                },
                'front_panel_byte_info': {
                    'gain': 1,
                    'source_channel': 1,
                },
                'rear_panel_byte_info': {
                    'rear_in_channel_num': 0,
                },
                'channels_bytes_info': {
                    'in_1': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'in_2': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'in_3': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'in_4': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'in_5': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'in_6': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'in_7': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'in_8': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'multiple_in_1': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'multiple_in_2': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'multiple_in_3': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                    'multiple_in_4': [
                        {'muscle_index': 0},
                        {'sensor_index': 0, 'adapter_index': 0},
                        {'side': 'not defined', 'high_pass_filter': 0.3, 'low_pass_filter': 130, 'mode': 'bipolar'},
                    ],
                },
            },
        },
        'glove_settings': {
            'ip': '127.0.0.1',
            'port': 53450,
        },
        'experiment_settings': {
            'repeats_number': 1,
            'rest_time_in_s': 1,
            'exercise_time_in_s': 1,
        },
    }

    @staticmethod
    def create(settings_dir: Path):
        settings_dir.parent.mkdir(exist_ok=True, parents=True)

        with open(settings_dir, mode='w') as json_file:
            json.dump(BasicSettingsCreater.basic_settings, json_file)
        

class SettingsData:
    
    def __init__(self, settings_dir: Path):

        self.__settings_dir = settings_dir
        self.__load_settings()
        
    
    def __getitem__(self, key: str):
        return self.__settings[key]


    @property
    def settings(self):
        return self.__settings
    

    def __load_settings(self):
        try:
            with open(self.__settings_dir, 'r') as json_file:
                self.__settings = json.load(json_file)
        except:
            BasicSettingsCreater.create(self.__settings_dir)
            self.__load_settings()
    

    def __save_settings(self, settings):
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                    mode='w', encoding='utf-8', dir=self.__settings_dir.parent,
                    prefix=self.__settings_dir.name + '.', suffix='.tmp', delete=False
                    ) as json_file:
                temporary_path = Path(json_file.name)
                json.dump(settings, json_file)
            os.replace(temporary_path, self.__settings_dir)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
    

    def update_settings(self, settings):
        updated_settings = deepcopy(settings)
        self.__save_settings(updated_settings)
        self.__settings = updated_settings
