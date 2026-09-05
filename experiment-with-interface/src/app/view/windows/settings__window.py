from typing import Callable, Dict

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QTabWidget, QScrollArea

from view.elements import VerticalLayout, TextField, PrimaryButton, DropdownList
from view.models import AppSettingsDataType, GloveSettingsDataType, ChannelSettingsDataType, MyographSettingsDataType, SettingsDataType


class SettingsWindow(QWidget):

    def __init__(
            self,
            labels: dict,
            myograph_settings_options: dict
            ):
        super().__init__()

        self.__labels = labels

        layout = VerticalLayout()
        self.tab_widget = QTabWidget()

        self.__app_settings_tab = AppSettingsTab(labels=self.__labels)
        self.tab_widget.addTab(self.__app_settings_tab, self.__labels['experiment_tab'])

        self.__glove_settings_tab = GloveSettingsTab(labels=self.__labels)
        self.tab_widget.addTab(self.__glove_settings_tab, self.__labels['glove_tab'])

        self.__myograph_settings_tab = MyographSettingsTab(
            labels=self.__labels,
            myograph_settings_options=myograph_settings_options
            )
        self.tab_widget.addTab(self.__myograph_settings_tab, self.__labels['myograph_tab'])

        layout.addWidget(self.tab_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(50)

        self.__back_button = PrimaryButton(self.__labels['back_button'])
        buttons_layout.addWidget(self.__back_button)

        self.__save_button = PrimaryButton(self.__labels['save_button'])
        buttons_layout.addWidget(self.__save_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    

    def add_callback_for_back_button(self, callback: Callable):
        self.__back_button.clicked.connect(callback)

    
    def add_callback_for_save_button(self, callback: Callable):
        self.__save_button.clicked.connect(callback)
    

    def get_all_settings(self) -> SettingsDataType:
        try:
            sets: SettingsDataType = {
                'app': self.__app_settings_tab.get_all_data(),
                'glove': self.__glove_settings_tab.get_all_data(),
                'myograph': self.__myograph_settings_tab.get_all_data()
            }
            self.__save_button.set_normal_style()
            return sets
        
        except BaseException as e:
            self.__save_button.set_error_style()
            raise e
    

    def set_all_fields_values(self, settings: SettingsDataType):
        self.__app_settings_tab.set_fields_values(settings['app'])
        self.__glove_settings_tab.set_fields_values(settings['glove'])
        self.__myograph_settings_tab.set_fields_values(settings['myograph'])


class AppSettingsTab(QWidget):

    def __init__(self, labels: dict):
        super().__init__()

        self.__labels = labels
        layout = VerticalLayout()

        self.__save_data_dir_field = TextField(
            field_hint=self.__labels['text_field_hint'],
            label_text=self.__labels['save_data_dir_field']
            )
        layout.addWidget(self.__save_data_dir_field)

        self.__number_of_exercise_repeats_field = TextField(
            field_hint=self.__labels['number_field_hint'],
            label_text=self.__labels['number_of_exercise_repeats_field'],
            field_data_type='number'
            )
        layout.addWidget(self.__number_of_exercise_repeats_field)
        
        self.__exercise_time_field = TextField(
            field_hint=self.__labels['number_field_hint'],
            label_text=self.__labels['exercise_time_field'],
            field_data_type='number'
            )
        layout.addWidget(self.__exercise_time_field)

        self.__rest_time_field = TextField(
            field_hint=self.__labels['number_field_hint'],
            label_text=self.__labels['rest_time_field'],
            field_data_type='number'
            )
        layout.addWidget(self.__rest_time_field)

        self.setLayout(layout)

    
    def get_save_data_dir(self) -> str:
        return self.__save_data_dir_field.validate_and_get_data()


    def get_number_of_exercise_repeats(self) -> int:
        value = self.__number_of_exercise_repeats_field.validate_and_get_data()
        return int(value) if value.isnumeric() else 0
    

    def get_exercise_time(self) -> int:
        value = self.__exercise_time_field.validate_and_get_data()
        return int(value) if value.isnumeric() else 0
    

    def get_rest_time(self) -> int:
        value = self.__rest_time_field.validate_and_get_data()
        return int(value) if value.isnumeric() else 0
    
    
    def get_all_data(self) -> AppSettingsDataType:
        return {
            'save_directory': self.get_save_data_dir(),
            'repeats_number': self.get_number_of_exercise_repeats(),
            'exercise_time_in_s': self.get_exercise_time(),
            'rest_time_in_s': self.get_rest_time()
        }
    
    def set_fields_values(self, settings: AppSettingsDataType):
        self.__save_data_dir_field.setFieldText(settings['save_directory'])
        self.__number_of_exercise_repeats_field.setFieldText(str(settings['repeats_number']))
        self.__exercise_time_field.setFieldText(str(settings['exercise_time_in_s']))
        self.__rest_time_field.setFieldText(str(settings['rest_time_in_s']))
    

class GloveSettingsTab(QWidget):

    def __init__(self, labels: dict):
        super().__init__()

        self.__labels = labels

        layout = VerticalLayout()

        self.__ip_address_field = TextField(
            field_hint=self.__labels['text_field_hint'],
            label_text=self.__labels['ip_address_field']
            )
        layout.addWidget(self.__ip_address_field)

        self.__port_field = TextField(
            field_hint=self.__labels['number_field_hint'],
            label_text=self.__labels['port_field'],
            field_data_type='number'
            )
        layout.addWidget(self.__port_field)

        self.setLayout(layout)

    
    def get_ip_address(self) -> str:
        return self.__ip_address_field.validate_and_get_data()


    def get_port(self) -> int:
        value = self.__port_field.validate_and_get_data()
        return int(value) if value.isnumeric() else 0
    
    
    def get_all_data(self) -> GloveSettingsDataType:
        return {
            'ip': self.get_ip_address(),
            'port': self.get_port()
        }
    

    def set_fields_values(self, settings: GloveSettingsDataType):
        self.__ip_address_field.setFieldText(settings['ip'])
        self.__port_field.setFieldText(str(settings['port']))


class ChannelSettingsBlock(QGroupBox):

    def __init__(
            self,
            channel_name: str,
            labels: dict,
            myograph_settings_options: dict
            ):
        super().__init__(title=channel_name)

        group_layout = VerticalLayout()

        self.__high_pass_filter_dropdown = DropdownList(
            myograph_settings_options['high_pass_filter_options'],
            label_text=labels['high_pass_filter']
            )
        group_layout.addWidget(self.__high_pass_filter_dropdown)

        self.__low_pass_filter_dropdown = DropdownList(
            myograph_settings_options['low_pass_filter_options'],
            label_text=labels['low_pass_filter']
            )
        group_layout.addWidget(self.__low_pass_filter_dropdown)

        self.__detection_mode_dropdown = DropdownList(
            myograph_settings_options['detecion_mode_options'],
            label_text=labels['detection_mode']
            )
        group_layout.addWidget(self.__detection_mode_dropdown)
        
        self.__electrodes_type_dropdown = DropdownList(
            myograph_settings_options['electrodes_type_options'],
            label_text=labels['electrodes_type']
            )
        group_layout.addWidget(self.__electrodes_type_dropdown)

        self.__adapter_type_dropdown = DropdownList(
            myograph_settings_options['adapter_type_options'],
            label_text=labels['adapter_type']
            )
        group_layout.addWidget(self.__adapter_type_dropdown)

        self.setLayout(group_layout)
    
    def get_channel_data(self) -> ChannelSettingsDataType:
        return {
            'sensor_index': self.__electrodes_type_dropdown.get_current_option_index(),
            'adapter_index': self.__adapter_type_dropdown.get_current_option_index(),
            'high_pass_filter': self.__high_pass_filter_dropdown.get_current_option_index(),
            'low_pass_filter': self.__low_pass_filter_dropdown.get_current_option_index(),
            'mode': self.__detection_mode_dropdown.get_current_option_index()
        }
    
    def set_channel_settings(self, channel_settings: ChannelSettingsDataType):
        self.__electrodes_type_dropdown.set_current_option_by_index(channel_settings['sensor_index'])
        self.__adapter_type_dropdown.set_current_option_by_index(channel_settings['adapter_index'])
        self.__high_pass_filter_dropdown.set_current_option_by_index(channel_settings['high_pass_filter'])
        self.__low_pass_filter_dropdown.set_current_option_by_index(channel_settings['low_pass_filter'])
        self.__detection_mode_dropdown.set_current_option_by_index(channel_settings['mode'])
        


class MyographSettingsTab(QWidget):

    def __init__(
            self,
            labels: dict,
            myograph_settings_options: dict
            ):
        super().__init__()

        layout = VerticalLayout()

        self.__labels = labels

        self.__ip_address_field = TextField(
            field_hint=self.__labels['text_field_hint'],
            label_text=self.__labels['ip_address_field']
            )
        layout.addWidget(self.__ip_address_field)

        self.__port_field = TextField(
            field_hint=self.__labels['number_field_hint'],
            label_text=self.__labels['port_field'],
            field_data_type='number'
            )
        layout.addWidget(self.__port_field)

        sampling_rate_opitions = ['512', '2048', '5120', '10240']
        self.__sampling_rate_dropdown = DropdownList(
            sampling_rate_opitions,
            label_text=self.__labels['sampling_rate']
            )
        layout.addWidget(self.__sampling_rate_dropdown)

        active_channels_opitions = [
            'IN1-2; Multiple IN1',
            'IN1-4; Multiple IN1-2',
            'IN1-6; Multiple IN1-3',
            'IN1-8; Multiple IN1-4'
        ]
        self.__active_in_channels_dropdown = DropdownList(
            active_channels_opitions,
            label_text=self.__labels['active_in_channels']
            )
        layout.addWidget(self.__active_in_channels_dropdown)
        
        self.__channels_groups: Dict[str, ChannelSettingsBlock] = dict()
        for channel_num in range(1, 9):
            channel_name = f'in_{channel_num}'
            channel_group = ChannelSettingsBlock(
                channel_name,
                labels=labels,
                myograph_settings_options=myograph_settings_options
                )
            self.__channels_groups[channel_name] = channel_group
            layout.addWidget(channel_group)
        
        for channel_num in range(1, 5):
            channel_name = f'multiple_in_{channel_num}'
            channel_group = ChannelSettingsBlock(
                channel_name,
                labels=labels,
                myograph_settings_options=myograph_settings_options
                )
            self.__channels_groups[channel_name] = channel_group
            layout.addWidget(channel_group)

        container_widget = QWidget()
        container_widget.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(container_widget)
        scroll_area.setWidgetResizable(True)
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
    

    def get_all_data(self) -> MyographSettingsDataType:
        return {
            'ip': self.__ip_address_field.validate_and_get_data(),
            'port': int(self.__port_field.validate_and_get_data()),
            'sampling_rate': self.__sampling_rate_dropdown.get_current_option_index(),
            'active_channels': self.__active_in_channels_dropdown.get_current_option_index(),
            'channels_settings': {channel_name: channel_group.get_channel_data() for channel_name, channel_group in self.__channels_groups.items()}
        }
    

    def set_fields_values(self, settings: MyographSettingsDataType):
        self.__ip_address_field.setFieldText(settings['ip'])
        self.__port_field.setFieldText(str(settings['port']))
        self.__active_in_channels_dropdown.set_current_option_by_index(settings['active_channels'])
        self.__sampling_rate_dropdown.set_current_option_by_index(settings['sampling_rate'])
        for channel_name, channel_settings in settings['channels_settings'].items():
            self.__channels_groups[channel_name].set_channel_settings(channel_settings)