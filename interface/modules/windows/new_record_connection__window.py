from typing import Callable

from PySide6.QtWidgets import QWidget, QGridLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from ..elements import VerticalLayout, PrimaryButton, SecondaryButton, Label
from ..constants import constants


class ConnectionWindow(QWidget):
    
    def __init__(
            self,
            connect_button_function: Callable,
            back_button_function: Callable,
            start_record_button_function: Callable
            ):
        super().__init__()

        layout = VerticalLayout()

        self.connect_button = PrimaryButton('подключиться к устройствам')
        self.connect_button.clicked.connect(connect_button_function)
        layout.addWidget(self.connect_button)

        info_grid = QGridLayout()
        info_grid.addWidget(
            QLabel('электромиограф:'),
            1,
            1,
            alignment=Qt.AlignmentFlag.AlignLeft
            )
        
        info_grid.addWidget(
            QLabel('перчатка:'),
            2,
            1,
            alignment=Qt.AlignmentFlag.AlignLeft
            )
        
        self.myograph_status = Label('')
        info_grid.addWidget(
            self.myograph_status,
            1,
            2,
            alignment=Qt.AlignmentFlag.AlignRight
            )
        
        self.glove_status = Label('')
        info_grid.addWidget(
            self.glove_status,
            2,
            2,
            alignment=Qt.AlignmentFlag.AlignRight
            )
        
        layout.addLayout(info_grid)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        self.back_button = SecondaryButton('назад')
        self.back_button.clicked.connect(back_button_function)
        buttons_layout.addWidget(self.back_button)
        self.start_record_button = SecondaryButton('начать запись')
        self.start_record_button.clicked.connect(start_record_button_function)
        buttons_layout.addWidget(self.start_record_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)


    def change_myogragh_status(self, text: str, is_connected: bool):
        self.myograph_status.setText(text)
        color = constants.active_color if is_connected else constants.error_color
        self.myograph_status.change_text_color(color)

    def change_glove_status(self, text: str, is_connected: bool):
        self.glove_status.setText(text)
        color = constants.active_color if is_connected else constants.error_color
        self.glove_status.change_text_color(color)