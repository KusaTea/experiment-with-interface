from typing import Callable

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt

from view.elements import VerticalLayout, SecondaryButton


class FinishWindow(QWidget):

    def __init__(self, labels: dict):
        super().__init__()

        layout = VerticalLayout()

        self.__labels = labels

        self.experiment_finish_label = QLabel(self.__labels['experiment_finish_label'])
        layout.addWidget(self.experiment_finish_label, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop))

        self.thanks_labels = QLabel(self.__labels['thanks_labels'])
        layout.addWidget(self.thanks_labels, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter))

        self.save_directory_label = QLabel(self.__labels['save_directory_label'])
        layout.addWidget(self.save_directory_label, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom))
        
        self.main_menu_button = SecondaryButton(self.__labels['main_menu_button'])
        layout.addWidget(self.main_menu_button, alignment=Qt.AlignmentFlag.AlignBottom)

        self.setLayout(layout)


    def add_callback_for_main_menu_button(self, callback: Callable):
        self.main_menu_button.clicked.connect(callback)


    def change_save_directory_label(self, directory: str):
        self.save_directory_label.setText(self.__labels['save_directory_label'] + directory)