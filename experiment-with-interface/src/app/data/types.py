from typing import TypedDict, Literal, Tuple


class AcquisitionByteDict(TypedDict):
    '''
    The first byte for the Quattrocento settings.

    :param decimator: if True all signals are recorded in sampling rate 10240 Hz and then transformed to required sampling rate
    :type decimator: bool
    :param start_record_with_trigger: set it True if you use some trigger to start record
    :type start_record_with_trigger: bool
    :param sampling_rate: sampling rate
    :type sampling_rate: Literal[512, 2048, 5120, 10240]
    :param active_channels: configure channels that provides data to analog output (see configuration protocol file) (3 to choose all channels)
    :type active_channel: int
    :param data_transfer_to_pc: True for data transfer from the device to PC
    :type data_transfer_to_pc: bool
    '''
    decimator: bool
    start_record_with_trigger: bool
    sampling_rate: Literal[512, 2048, 5120, 10240]
    channels_for_analog_output: Literal[0, 1, 2, 3]
    data_transfer_to_pc: bool


class FrontPanelByteDict(TypedDict):
    '''
    The second byte for the Quattrocento settings.

    :param gain: output gain
    :type gain: Literal[1, 2, 4, 16]
    :param source_channel: possible values: 0-12 (see the configuration protocol file for more details)
    :type source_channel: int
    '''
    gain: Literal[1, 2, 4, 16]
    source_channel: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]


class RearPanelByteDict(TypedDict):
    '''
    The third byte for the Quattrocento settings.

    :param rear_in_channel_num: source of the data from the rear panel (0-15)
    :type rear_in_channel_num: int
    '''
    rear_in_channel_num: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


class ChannelMuscleByteDict(TypedDict):
    '''
    This byte configures the muscle from which signal will be recorded

    :param muscle_index: index of a target muscle (0-64) (see the configuration protocol file for more details)
    :type muscle_index: int
    '''
    muscle_index: int


class ChannelElectrodeAdapterByteDict(TypedDict):
    '''
    This byte configures the electrode and the adapter which will be used

    :param sensor_index: index of an electrode (0-23) (see the configuration protocol file for more details)
    :type sensor_index: int
    :param adapter_index: index of an adapter (0-6) (see the configuration protocol file for more details)
    :type adapter_index: int
    '''
    sensor_index: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    adapter_index: Literal[0, 1, 2, 3, 4, 5, 6]


class ChannelLastByteDict(TypedDict):
    '''
    This byte configures body side, high pass filter threshold, low pass filter threshold and record mode

    :param side: body side
    :type side: Literal["not defined", "right", "left", None]
    :param high_pass_filter: high pass filter threshold value
    :type high_pass_filter: Literal[0.3, 10, 100, 200]
    :param low_pass_filter: low pass filter threshold value
    :type low_pass_filter: Literal[130, 500, 900, 4400]
    :param mode: lead type
    :type mode: Literal["monopolar", "differential", "bipolar"]
    '''

    side: Literal["not defined", "right", "left", None]
    high_pass_filter: Literal[0.3, 10, 100, 200]
    low_pass_filter: Literal[130, 500, 900, 4400]
    mode: Literal["monopolar", "differential", "bipolar"]


channel_info_tuple = Tuple[ChannelMuscleByteDict, ChannelElectrodeAdapterByteDict, ChannelLastByteDict]

class ChannelsBytesDict(TypedDict):
    '''
    This dict defines configuration parameters for each channel

    :keys: in_1, in_2, in_3, in_4, in_5, in_6, in_7, in_8, multiple_in_1, multiple_in_2, multiple_in_3, multiple_in_4
    :values: Tuple[ChannelMuscleByteDict, ChannelElectrodeAdapterByteDict, ChannelLastByteDict]
    '''

    in_1: channel_info_tuple
    in_2: channel_info_tuple
    in_3: channel_info_tuple
    in_4: channel_info_tuple
    in_5: channel_info_tuple
    in_6: channel_info_tuple
    in_7: channel_info_tuple
    in_8: channel_info_tuple
    multiple_in_1: channel_info_tuple
    multiple_in_2: channel_info_tuple
    multiple_in_3: channel_info_tuple
    multiple_in_4: channel_info_tuple


class OptionsDict(TypedDict):
    '''
    This byte configures body side, high pass filter threshold, low pass filter threshold and record mode

    :param acquisition_byte_info:
    :type acquisition_byte_info: AcquisitionByteDict
    :param analog_output_first_byte_info:
    :type analog_output_first_byte_info: FrontPanelByteDict
    :param analog_output_second_byte_info:
    :type analog_output_second_byte_info: RearPanelByteDict
    :param channels_bytes_info:
    :type channels_bytes_info: ChannelsBytesDict
    '''
    acquisition_byte_info: AcquisitionByteDict
    front_panel_byte_info: FrontPanelByteDict
    rear_panel_byte_info: RearPanelByteDict
    channels_bytes_info: ChannelsBytesDict