from typing import Callable

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt

from ..elements import VerticalLayout, SecondaryButton


class FinishWindow(QWidget):

    def __init__(self):
        super().__init__()

        layout = VerticalLayout()

        layout.addWidget(QLabel('эксперимент окончен'), alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop))
        layout.addWidget(QLabel('СПАСИБО ЗА УЧАСТИЕ!'), alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter))
        self.save_directory_label = QLabel('сохраненный файл:\n')
        layout.addWidget(self.save_directory_label, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom))
        
        self.main_menu_button = SecondaryButton('главное меню')
        layout.addWidget(self.main_menu_button, alignment=Qt.AlignmentFlag.AlignBottom)

        self.setLayout(layout)


    def add_callback_for_main_menu_button(self, callback: Callable):
        self.main_menu_button.clicked.connect(callback)


    def change_save_directory_label(self, directory: str):
        self.save_directory_label.setText('сохраненный файл:\n' + directory)