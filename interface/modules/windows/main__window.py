from typing import Callable

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from ..elements import VerticalLayout, SecondaryButton


class MainWindow(QWidget):

    def __init__(
            self,
            new_record_button_function: Callable,
            settings_button_function: Callable
            ):
        super().__init__()

        self.new_record_button = SecondaryButton('НОВАЯ ЗАПИСЬ')
        self.new_record_button.clicked.connect(new_record_button_function)
        
        self.settings_button = SecondaryButton('НАСТРОЙКИ')
        self.settings_button.clicked.connect(settings_button_function)

        layout = VerticalLayout()
        layout.addWidget(self.new_record_button, alignment=(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter))
        layout.addWidget(self.settings_button, alignment=(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter))

        self.setLayout(layout)