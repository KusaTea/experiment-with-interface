import json
import pathlib

current_path = pathlib.Path()
save_directory = current_path / 'data'

myograph_ip = '169.254.1.10'
myograph_port = 23456

standard_channel_tuple = (
        {"muscle_index": 0},
        {"sensor_index": 0, "adapter_index": 0},
        {"side": "not defined", "high_pass_filter": 0.3, "low_pass_filter": 130, "mode": "bipolar"}
    )

record_channel_tuple = (
    {"muscle_index": 0},
    {"sensor_index": 12, "adapter_index": 4},
    {"side": "not defined", "high_pass_filter": 10, "low_pass_filter": 500, "mode": "monopolar"}
)
    
myograph_options = {
    'acquisition_byte_info': {
        'decimator': False,
        'start_record_with_trigger': False,
        'sampling_rate': 2048,
        'channels_for_analog_output': 1,
        'data_transfer_to_pc': True
    },
    'front_panel_byte_info': {
        'gain': 1,
        'source_channel': 1
    },
    'rear_panel_byte_info': {
        'rear_in_channel_num': 0
    },
    'channels_bytes_info': {
        'in_1': standard_channel_tuple,
        'in_2': standard_channel_tuple,
        'in_3': standard_channel_tuple,
        'in_4': standard_channel_tuple,
        'in_5': standard_channel_tuple,
        'in_6': standard_channel_tuple,
        'in_7': standard_channel_tuple,
        'in_8': standard_channel_tuple,
        'multiple_in_1': record_channel_tuple,
        'multiple_in_2': record_channel_tuple,
        'multiple_in_3': standard_channel_tuple,
        'multiple_in_4': standard_channel_tuple
        }
    }

glove_ip = '127.0.0.1'
glove_port = 53450

settings = {
    'save_directory': str(save_directory.absolute()),
    'myograph_settings': {
        'ip': myograph_ip,
        'port': myograph_port,
        'options': myograph_options,
    },
    'glove_settings': {
        'ip': glove_ip,
        'port': glove_port
    },
    'experiment_settings': {
        'repeats_number': 5,
        'rest_time_in_s': 10,
        'exercise_time_in_s': 5 
    }
}

with open(current_path / 'settings.json', 'w') as settings_file:
    json.dump(settings, settings_file)