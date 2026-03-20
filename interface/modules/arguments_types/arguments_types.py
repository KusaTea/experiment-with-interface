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


ElectromyographSettingsType = List[DropDownInfoType]


class SettingsWindowArgumentsType(TypedDict):
    myograph_settings: ElectromyographSettingsType


class PatientWindowArgumentsType(TypedDict):
    patient_info_options: PatientInfoOptionsType


class ExperimentWindowArgumentsType(TypedDict):
    bar_info: BarInfoType


class StackedWindowsArgumentsType(TypedDict):
    settings_window_arguments: SettingsWindowArgumentsType
    patient_window_arguments: PatientWindowArgumentsType
    experiment_window_arguments: ExperimentWindowArgumentsType