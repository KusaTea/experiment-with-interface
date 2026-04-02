from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFontMetrics

from ..constants import constants


_primary_style = '''
QPushButton {{
    padding: 10px;
    background-color: {background_color};
    color: {text_color};
    border: none;
    border-radius: 10px;
}}

QPushButton:hover {{
    background-color: {hover_color};
}}

QPushButton:focus {{
    border: 2px solid {outline_color};
    outline: none;
}}

QPushButton:pressed {{
    background-color: {active_color};
}}
'''

_secondary_style = '''
QPushButton {{
    padding: 10px;
    background-color: {background_color};
    color: {text_color};
    border: 1px solid {border_color};
    border-radius: 10px;
}}

QPushButton:hover {{
    border-color: {hover_color};
}}

QPushButton:focus {{
    border: 2px solid {outline_color};
    outline: none;
}}

QPushButton:pressed {{
    background-color: {active_color};
    color: {active_text_color};
}}
'''.format(
    background_color=constants.transparent,
    border_color=constants.active_color,
    text_color=constants.active_color,
    hover_color=constants.hover_color,
    outline_color=constants.outline_color,
    active_color=constants.active_color,
    active_text_color=constants.primary_color
)


class PrimaryButton(QPushButton):

    def __init__(self, text):
        super().__init__(text)

        self.setStyleSheet(
            _primary_style.format(
                background_color=constants.primary_color,
                text_color=constants.text_color,
                hover_color=constants.hover_color,
                outline_color=constants.outline_color,
                active_color=constants.active_color
                )
            )

        text_width = QFontMetrics(self.font()).horizontalAdvance(text)
        
        self.setMinimumSize(max(100, text_width + 30), 50)
        self.setMaximumSize(max(250, text_width + 30), 100)
    
    def set_error_style(self):
        self.setStyleSheet(
            _primary_style.format(
                background_color=constants.error_color,
                text_color=constants.text_color,
                hover_color=constants.hover_color,
                outline_color=constants.outline_color,
                active_color=constants.active_color
                )
            )
    
    def set_normal_style(self):
        self.setStyleSheet(
            _primary_style.format(
                background_color=constants.primary_color,
                text_color=constants.text_color,
                hover_color=constants.hover_color,
                outline_color=constants.outline_color,
                active_color=constants.active_color
                )
            )


class SecondaryButton(PrimaryButton):

    def __init__(self, text):
        super().__init__(text)

        self.setStyleSheet(_secondary_style)
        self.setMinimumSize(50, 50)
        self.setMaximumSize(250, 100)