from ..arguments_types import qtpe
from . import quattrocento_transform_dicts as qtdicts


class QuattrocentoSettings:

    def __init__(self, options: qtpe.OptionsDict):
        self.acquisition_byte = self.construct_acquire_byte(options['acquisition_byte_info'])
        self.front_panel_byte = self.construct_front_panel_byte(options['front_panel_byte_info'])
        self.rear_panel_byte = self.construct_rear_panel_byte(options['rear_panel_byte_info'])
        self.channels_bytes = self.get_channels_bytes_list(options['channels_bytes_info'])

        self.sampling_rate = options['acquisition_byte_info']['sampling_rate']
        num_of_channels_list = [120, 216, 312, 408]
        self.num_of_channels = num_of_channels_list[options['acquisition_byte_info']['channels_for_analog_output']]
        self.buffer_size = 2 * self.num_of_channels * self.sampling_rate
        self.mV_constant = 5 / (2 ** 16) / 150 * 1000


    def get_bytes(self) -> bytes:
        self.settings_bytes = self.concat()
        results = self.settings_bytes + [self.calculate_crc_8(self.settings_bytes)]
        return self.transform_binary_to_bytes(self.transform_list_to_binary(results))


    def concat(self):
        sets = [self.acquisition_byte, self.front_panel_byte, self.rear_panel_byte] + self.channels_bytes
        return sets


    def calculate_crc_8(self, vector: list) -> int:
        crc = 0
        for byte in vector:

            for _ in range(8):
                sum = 0 if crc % 2 == byte % 2 else 1
                crc = crc // 2

                if sum > 0:
                    s = ['0' for i in range(8)]
                    a = format(crc, '08b')
                    b = format(140, '08b')
                    for k in range(8):
                        s[k] = '0' if a[k] == b[k] else '1'

                    crc = int(''.join(s), 2)
                byte = byte // 2
        return crc


    def transform_list_to_binary(self, values: list) -> str:
        return ''.join([format(num, '08b') for num in values])


    def transform_binary_to_bytes(self, binary: str) -> bytes:
        dec = int(binary, 2)
        dec = dec.to_bytes(40, byteorder="big")
        return dec


    def construct_acquire_byte(self, acquire_byte_info: qtpe.AcquisitionByteDict) -> int:
        decimator_encoded = int(acquire_byte_info['decimator']) * 64
        record_encoded = int(acquire_byte_info['start_record_with_trigger']) * 32
        sampling_rate_encoded = qtdicts.sampling_rate_transform_dict[acquire_byte_info['sampling_rate']]
        channels_encoded = acquire_byte_info['channels_for_analog_output'] * 2
        acquiring_encoded = int(acquire_byte_info['data_transfer_to_pc'])
        return 128 + decimator_encoded + record_encoded + sampling_rate_encoded \
            + channels_encoded + acquiring_encoded


    def construct_front_panel_byte(self, front_panel_byte_info: qtpe.FrontPanelByteDict) -> int:
        assert 0 <= front_panel_byte_info['source_channel'] <= 12, 'Wrong number of channel was given. It has to be in range [0, 12]'
        assert front_panel_byte_info['gain'] in {1, 2, 4, 16}, 'Wrong number for analog output gain was given. List of possible values: 1, 2, 4, 16'

        return qtdicts.analog_output_gain_transform_dict[front_panel_byte_info['gain']] + front_panel_byte_info['source_channel']


    def construct_rear_panel_byte(self, rear_panel_byte_info: qtpe.RearPanelByteDict) -> int:
        assert 0 <= rear_panel_byte_info['rear_in_channel_num'] <= 16, 'Wrong number of channels for output was given. It has to be in range [0, 16]'
        return rear_panel_byte_info['rear_in_channel_num']


    def get_channels_bytes_list(self, channels: qtpe.ChannelsBytesDict) -> list[int]:
        return self.construct_channel_byte(*channels['in_1']) +\
            self.construct_channel_byte(*channels['in_2']) +\
            self.construct_channel_byte(*channels['in_3']) +\
            self.construct_channel_byte(*channels['in_4']) +\
            self.construct_channel_byte(*channels['in_5']) +\
            self.construct_channel_byte(*channels['in_6']) +\
            self.construct_channel_byte(*channels['in_7']) +\
            self.construct_channel_byte(*channels['in_8']) +\
            self.construct_channel_byte(*channels['multiple_in_1']) +\
            self.construct_channel_byte(*channels['multiple_in_2']) +\
            self.construct_channel_byte(*channels['multiple_in_3']) +\
            self.construct_channel_byte(*channels['multiple_in_4'])


    def construct_channel_byte(self, muscle_byte: qtpe.ChannelMuscleByteDict, electrode_adapter_byte: qtpe.ChannelElectrodeAdapterByteDict, last_byte: qtpe.ChannelLastByteDict) -> list:
        assert 0 <= muscle_byte['muscle_index'] <= 64, 'Wrong index of muscle was given. It has to be in range [0, 64]'
        assert 0 <= electrode_adapter_byte['sensor_index'] <= 23, 'Wrong index of electrodes was given. It has to be in range [0, 23]'
        assert 0 <= electrode_adapter_byte['adapter_index'] <= 6, 'Wrong index of adapter was given. It has to be in range [0, 6]'
        assert last_byte['high_pass_filter'] in {0.3, 10, 100, 200}, 'Wrong value for high pass filter threshold was provided. Try one of these: 0.3, 10, 100, 200'
        assert last_byte['low_pass_filter'] in {130, 500, 900, 4400}, 'Wrong value for low pass filter threshold was provided. Try one of these: 130, 500, 900, 4400'
        assert last_byte['mode'] in {"monopolar", "differential", "bipolar"}, 'Wrong value for mode was provided. Possible modes: Monopolar, Differential, Bipolar'

        electrode_type_encoded = electrode_adapter_byte['sensor_index'] * 2 ** 3
        side_encoded = qtdicts.side_transform_dict[last_byte['side']]
        high_pass_filter_threshold_encoded = qtdicts.high_pass_filter_threshold_transform_dict[last_byte['high_pass_filter']]
        low_pass_filter_threshold_encoded = qtdicts.low_pass_filter_threshold_transform_dict[last_byte['low_pass_filter']]
        lead_mode_encoded = qtdicts.lead_mode_transform_dict[last_byte['mode']]

        first_channel_byte = muscle_byte['muscle_index']
        second_channel_byte = electrode_type_encoded + electrode_adapter_byte['adapter_index']
        third_channel_byte = side_encoded + high_pass_filter_threshold_encoded \
            + low_pass_filter_threshold_encoded + lead_mode_encoded

        return [first_channel_byte, second_channel_byte, third_channel_byte]
