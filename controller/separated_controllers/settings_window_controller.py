from typing import Callable

from interface.modules.stacked_windows import StackedWindows
from model.settings_data import SettingsData

from_raw_transform_dicts = {
    'sampling_rate': {
        0: 512,
        1: 2048,
        2: 5120,
        3: 10240
    },

    'high_pass_filter_threshold': {
        0: 0.3,
        1: 10,
        2: 100,
        3: 200
    },

    'low_pass_filter_threshold': {
        0: 130,
        1: 500,
        2: 900,
        3: 4400
    },

    'mode': {
        0: 'bipolar',
        1: 'monopolar',
        2: 'differential'
    }
}

to_raw_transform_dict = {
    key: {
        param_val: param_key for param_key, param_val in dct.items()
        } for key, dct in from_raw_transform_dicts.items()
    }


class SettingsWindowController:

    def __init__(self, stacked_windows: StackedWindows, settings: SettingsData, additional_callback_for_save_button: Callable = lambda: None):
        self.__stacked_windows = stacked_windows
        self.__settings = settings.settings
        self.__additional_callback_for_save_button = additional_callback_for_save_button
        
        self.__settings_window = self.__stacked_windows.settings_window
        self.__settings_window.add_callback_for_back_button(self.__callback_for_back_button)
        self.__settings_window.add_callback_for_save_button(self.__callback_for_save_button)

        self.__settings_window.set_all_fields_values(self.__transform_settings_to_raw())

    
    def __callback_for_back_button(self):
        self.__stacked_windows.display_main_menu()
        self.__settings_window.set_all_fields_values(self.__transform_settings_to_raw())

    
    def __callback_for_save_button(self):
        self.__transform_settings_from_raw()
        self.__stacked_windows.display_main_menu()
        self.__additional_callback_for_save_button(self.__settings)
    

    def __transform_settings_from_raw(self):
        try:
            fields_values = self.__settings_window.get_all_settings()

            self.__settings['save_directory'] = fields_values['app']['save_directory']
            self.__settings['experiment_settings'] = {
                'repeats_number': fields_values['app']['repeats_number'],
                'rest_time_in_s': fields_values['app']['rest_time_in_s'],
                'exercise_time_in_s': fields_values['app']['exercise_time_in_s']
                }
            
            self.__settings['glove_settings'] = fields_values['glove']

            self.__settings['myograph_settings']['ip'] = fields_values['myograph']['ip']
            self.__settings['myograph_settings']['port'] = fields_values['myograph']['port']
            self.__settings['myograph_settings']['options']['acquisition_byte_info']['sampling_rate'] = from_raw_transform_dicts['sampling_rate'][fields_values['myograph']['sampling_rate']]
            self.__settings['myograph_settings']['options']['acquisition_byte_info']['channels_for_analog_output'] = fields_values['myograph']['active_channels']

            for channel_name, channel_settings in fields_values['myograph']['channels_settings'].items():
                self.__settings['myograph_settings']['options']['channels_bytes_info'][channel_name][1]['sensor_index'] = channel_settings['sensor_index']
                self.__settings['myograph_settings']['options']['channels_bytes_info'][channel_name][1]['adapter_index'] = channel_settings['adapter_index']

                self.__settings['myograph_settings']['options']['channels_bytes_info'][channel_name][2]['high_pass_filter'] = from_raw_transform_dicts['high_pass_filter_threshold'][channel_settings['high_pass_filter']]
                self.__settings['myograph_settings']['options']['channels_bytes_info'][channel_name][2]['low_pass_filter'] = from_raw_transform_dicts['low_pass_filter_threshold'][channel_settings['low_pass_filter']]
                self.__settings['myograph_settings']['options']['channels_bytes_info'][channel_name][2]['mode'] = from_raw_transform_dicts['mode'][channel_settings['mode']]

        except:
            pass

    
    def __transform_settings_to_raw(self):
        return {
            'app': {
                'save_directory': self.__settings['save_directory'],
                'repeats_number': self.__settings['experiment_settings']['repeats_number'],
                'rest_time_in_s': self.__settings['experiment_settings']['rest_time_in_s'],
                'exercise_time_in_s': self.__settings['experiment_settings']['exercise_time_in_s']
            },

            'glove': self.__settings['glove_settings'],

            'myograph': {
                'ip': self.__settings['myograph_settings']['ip'],
                'port': self.__settings['myograph_settings']['port'],
                'sampling_rate': to_raw_transform_dict['sampling_rate'][self.__settings['myograph_settings']['options']['acquisition_byte_info']['sampling_rate']],
                'active_channels': self.__settings['myograph_settings']['options']['acquisition_byte_info']['channels_for_analog_output'],
                'channels_settings': {
                    channel_name: {
                        'sensor_index': channel_settings[1]['sensor_index'],
                        'adapter_index': channel_settings[1]['adapter_index'],
                        'high_pass_filter': to_raw_transform_dict['high_pass_filter_threshold'][channel_settings[2]['high_pass_filter']],
                        'low_pass_filter': to_raw_transform_dict['low_pass_filter_threshold'][channel_settings[2]['low_pass_filter']],
                        'mode': to_raw_transform_dict['mode'][channel_settings[2]['mode']]
                    } for channel_name, channel_settings in self.__settings['myograph_settings']['options']['channels_bytes_info'].items()
                }
            }
        }

