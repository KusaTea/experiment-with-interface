from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt


class VerticalLayout(QVBoxLayout):

    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setContentsMargins(100, 100, 100, 100)
        self.setSpacing(30)