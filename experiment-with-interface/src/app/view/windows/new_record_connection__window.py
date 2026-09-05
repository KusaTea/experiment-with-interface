from typing import Callable

from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from view.elements import VerticalLayout, PrimaryButton, SecondaryButton, Label
from view import constants


class ConnectionWindow(QWidget):
    
    def __init__(self, labels: dict):
        super().__init__()

        self.__labels = labels

        layout = VerticalLayout()

        self.connect_button = PrimaryButton(self.__labels['connect_button'])
        layout.addWidget(self.connect_button)

        info_grid = QGridLayout()

        self.myograph_label = QLabel(self.__labels['myograph_label'])
        info_grid.addWidget(
            self.myograph_label,
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignLeft
            )

        self.glove_label = QLabel(self.__labels['glove_label'])
        info_grid.addWidget(
            self.glove_label,
            2,
            1,
            alignment=Qt.AlignmentFlag.AlignLeft
            )
        
        self.myograph_status = Label(self.__labels['not_connected'])
        info_grid.addWidget(
            self.myograph_status,
            1,
            2,
            alignment=Qt.AlignmentFlag.AlignRight
            )
        
        self.glove_status = Label(self.__labels['not_connected'])
        info_grid.addWidget(
            self.glove_status,
            2,
            2,
            alignment=Qt.AlignmentFlag.AlignRight
            )
        
        layout.addLayout(info_grid)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        self.back_button = SecondaryButton(self.__labels['back_button'])
        buttons_layout.addWidget(self.back_button)
        self.start_record_button = SecondaryButton(self.__labels['start_record_button'])
        buttons_layout.addWidget(self.start_record_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)


    def add_callback_for_connect_button(self, callback: Callable):
        self.connect_button.clicked.connect(callback)

    
    def add_callback_for_back_button(self, callback: Callable):
        self.back_button.clicked.connect(callback)


    def add_callback_for_start_record_button(self, callback: Callable):
        self.start_record_button.clicked.connect(callback)


    def change_myogragh_status(self, is_connected: bool):
        self.myograph_status.setText(self.__labels['connected' if is_connected else 'not_connected'])
        color = constants.active_color if is_connected else constants.error_color
        self.myograph_status.change_text_color(color)


    def change_glove_status(self, is_connected: bool):
        self.glove_status.setText(self.__labels['connected' if is_connected else 'not_connected'])
        color = constants.active_color if is_connected else constants.error_color
        self.glove_status.change_text_color(color)
    

    def reset(self):
        self.change_myogragh_status(False)
        self.change_glove_status(False)