from typing import TypedDict, List, Callable


class BarInfoType(TypedDict):
    min_value: int
    max_value: int


class PatientInfoOptionsType(TypedDict):
    gender_options: List[str]
    hand_options: List[str]


class DropDownInfoType(TypedDict):
    title: str
    items: List[str]
    default_option: str


class SettingsWindowArgumentsType(TypedDict):
    myograph_settings_options: dict


class PatientWindowArgumentsType(TypedDict):
    patient_info_options: PatientInfoOptionsType


class ExperimentWindowArgumentsType(TypedDict):
    bar_info: BarInfoType


class StackedWindowsArgumentsType(TypedDict):
    labels: dict
    patient_window_arguments: PatientWindowArgumentsType
    experiment_window_arguments: ExperimentWindowArgumentsType
    settings_window_arguments: SettingsWindowArgumentsType