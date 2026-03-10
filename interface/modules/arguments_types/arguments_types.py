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


class MainWindowArgumentsType(TypedDict):
    new_record_button_function: Callable
    settings_button_function: Callable


class SettingsWindowArgumentsType(TypedDict):
    back_button_function: Callable
    save_button_function: Callable
    myograph_settings: ElectromyographSettingsType


class PatientWindowArgumentsType(TypedDict):
    back_button_function: Callable
    next_button_function: Callable
    patient_info_options: PatientInfoOptionsType


class ConnectionWindowArgumentsType(TypedDict):
    connect_button_function: Callable
    back_button_function: Callable
    start_record_button_function: Callable


class ExperimentWindowArgumentsType(TypedDict):
    bar_info: BarInfoType


class FinishWindowArgumentsType(TypedDict):
    main_menu_button_function: Callable


class StackedWindowsArgumentsType(TypedDict):
    main_window_arguments: MainWindowArgumentsType
    settings_window_arguments: SettingsWindowArgumentsType
    patient_window_arguments: PatientWindowArgumentsType
    connection_window_arguments: ConnectionWindowArgumentsType
    experiment_window_arguments: ExperimentWindowArgumentsType
    finish_window_arguments: FinishWindowArgumentsType