from typing import TypedDict


class AppSettingsDataType(TypedDict):
    save_directory: str
    repeats_number: int
    rest_time_in_s: int
    exercise_time_in_s: int


class GloveSettingsDataType(TypedDict):
    ip: str
    port: int


class ChannelSettingsDataType(TypedDict):
    sensor_index: int
    adapter_index: int
    high_pass_filter: int
    low_pass_filter: int
    mode: int


class MyographSettingsDataType(TypedDict):
    ip: str
    port: int
    sampling_rate: int
    active_channels: int
    channels_settings: dict


class SettingsDataType(TypedDict):
    app: AppSettingsDataType
    glove: GloveSettingsDataType
    myograph: MyographSettingsDataType