from os import PathLike

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from ..elements import VerticalLayout, ProgressBar
from ..arguments_types import BarInfoType


class ExperimentWindow(QWidget):

    def __init__(
            self,
            bar_info: BarInfoType
            ):
        super().__init__()

        layout = VerticalLayout()

        self.progress_bar = ProgressBar(
            minimum=bar_info['min_value'],
            maximum=bar_info['max_value'],
            start_value=bar_info['min_value']
            )
        self.progress_bar.setMinimumWidth(500)
        layout.addWidget(self.progress_bar, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop))

        self.event_label = QLabel('')
        layout.addWidget(self.event_label, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter))

        self.timer = QLabel('')
        layout.addWidget(self.timer, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter))

        self.exercise_label = QLabel('')
        layout.addWidget(self.exercise_label, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter))
        
        self.exercise_image = QLabel('')
        layout.addWidget(self.exercise_image, alignment=(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter))

        self.setLayout(layout)
    

    def change_progress(self, step: int = 1):
        self.progress_bar.increase(step)


    def change_event(self, text: str):
        self.event_label.setText(text)


    def change_timer(self, text: str):
        self.timer.setText(text)


    def change_exercise(self, new_exercise_name: str, new_exercise_image_dir: PathLike[str]):
        self.exercise_label.setText(new_exercise_name)
        self.exercise_image.setPixmap(QPixmap(new_exercise_image_dir))

    
    def change_bar_info(self, min_value: int, max_value: int):
        self.progress_bar.changeMinMaxValues(min_value, max_value)