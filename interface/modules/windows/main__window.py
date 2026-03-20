from typing import Callable

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

from ..elements import VerticalLayout, SecondaryButton


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.new_record_button = SecondaryButton('НОВАЯ ЗАПИСЬ')
        
        
        self.settings_button = SecondaryButton('НАСТРОЙКИ')

        layout = VerticalLayout()
        layout.addWidget(self.new_record_button, alignment=(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter))
        layout.addWidget(self.settings_button, alignment=(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter))

        self.setLayout(layout)
    

    def add_callback_for_new_record_button(self, callback: Callable):
        self.new_record_button.clicked.connect(callback)
    

    def add_callback_for_settings_button(self, callback: Callable):
        self.settings_button.clicked.connect(callback)