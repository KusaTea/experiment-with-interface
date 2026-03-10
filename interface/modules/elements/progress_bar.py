from PySide6.QtWidgets import QProgressBar

from ..constants import constants

_style = '''
QProgressBar {{
    border: 2px solid {background_color};
    border-radius: 10px;
    text-align: center;
    color: {text_color};
    background-color: rgba(0, 0, 0, 0)
}}

QProgressBar::chunk {{
    border-radius: 10px;
    background-color: {progress_color};
}}
'''.format(
    background_color=constants.text_color,
    text_color=constants.text_color,
    progress_color=constants.primary_color
)

class ProgressBar(QProgressBar):

    def __init__(self, minimum: int, maximum: int, start_value: int = 0):
        super().__init__()

        self.setStyleSheet(_style)

        self.setRange(minimum, maximum)
        self.setValue(start_value)

        self.setFormat('%v / %m')
    
    def increase(self, step: int = 1):
        self.setValue(self.value() + step)
