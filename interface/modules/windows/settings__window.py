from typing import Callable

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox
from PySide6.QtCore import Qt

from ..elements import VerticalLayout, TextField, PrimaryButton, SecondaryButton, DropdownList
from ..arguments_types import ElectromyographSettingsType


class SettingsWindow(QWidget):

    def __init__(
            self,
            myograph_settings: ElectromyographSettingsType
            ):
        super().__init__()

        layout = VerticalLayout()

        directory_layout = QHBoxLayout()
        directory_layout.setSpacing(10)
        self.directory_field = TextField(field_hint='введите текст...', label_text='директория базы данных')
        directory_layout.addWidget(self.directory_field, stretch=3, alignment=Qt.AlignmentFlag.AlignBottom)
        self.directory_button = PrimaryButton('выбрать')
        directory_layout.addWidget(self.directory_button, stretch=1, alignment=Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(directory_layout)

        myograph_layout = QVBoxLayout()
        myograph_layout.setSpacing(10)

        self.myograph_address_field = TextField(field_hint='введите текст...', label_text='ip:port')
        myograph_layout.addWidget(self.myograph_address_field)

        # self.myograph_dropdowns = list()
        # for dropdown_dict in myograph_settings:
        #     dropdown = DropdownList(dropdown_items=dropdown_dict['items'], label_text=dropdown_dict['title'])
        #     dropdown.setCurrentOption(dropdown_dict['items'].index(dropdown_dict['default_option']))
        #     myograph_layout.addWidget(dropdown)
        #     self.myograph_dropdowns.append(dropdown)
        # myograph_group = QGroupBox(title='настройки элетктромиографа', checkable=False)
        # myograph_group.setLayout(myograph_layout)
        # layout.addWidget(myograph_group)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(50)
        self.back_button = SecondaryButton('назад')
        buttons_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.save_button = SecondaryButton('сохранить')
        buttons_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(buttons_layout)
    
        self.setLayout(layout)

    # TODO: finish function
    def changeValues(self, values: dict[str, str]):
        self.directory_field.setFieldText(values['directory_field'])
        pass


    def add_callback_for_back_button(self, callback: Callable):
        self.back_button.clicked.connect(callback)

    
    def add_callback_for_save_button(self, callback: Callable):
        self.save_button.clicked.connect(callback)