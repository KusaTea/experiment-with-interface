from PySide6.QtWidgets import QLabel

from ..constants import constants

_style_sample = '''
    QLabel {{
        color: {text_color};
    }}
'''

_normal_style = _style_sample.format(text_color=constants.text_color)


class Label(QLabel):

    def __init__(self, text: str):
        super().__init__(text)
        
        self.setStyleSheet(_normal_style)


    def change_text_color(self, color: str):
        self.setStyleSheet(_style_sample.format(text_color=color))


    def reset_style(self):
        self.setStyleSheet(_normal_style)