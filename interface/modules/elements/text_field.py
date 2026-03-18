from typing import Literal
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout

from ..constants import constants

_normal_style = '''
    QLineEdit {{
        border: 1px solid {border_color};
        background-color: {backgroud_color};
    }}
'''.format(
    border_color=constants.active_color,
    backgroud_color=constants.transparent
)

_error_style = '''
    QLineEdit {{
        border: 1px solid {border_color};
        background-color: {backgroud_color};
    }}
'''.format(
    border_color=constants.error_color,
    backgroud_color=constants.transparent
)

class TextField(QWidget):

    def __init__(self, field_hint: str = '', label_text: str = '', field_data_type: Literal['text', 'number'] = 'text'):
        super().__init__()

        self.setStyleSheet(_normal_style)
        self.field_data_type = field_data_type

        layout = QVBoxLayout()

        layout.setSpacing(5)
        
        self.field_label = QLabel(label_text)
        layout.addWidget(self.field_label)
        self.field = QLineEdit()
        self.field.setPlaceholderText(field_hint)
        layout.addWidget(self.field)

        self.setLayout(layout)


    def setFieldText(self, text: str):
        self.field.setText(text)
    

    def reset(self):
        self.setFieldText('')


    def getFieldText(self):
        return self.field.text()
    

    def make_normal_style(self):
        self.setStyleSheet(_normal_style)


    def make_error_style(self):
        self.setStyleSheet(_error_style)


    def validate_data(self):
        if self.field_data_type == 'text':
            return len(self.getFieldText()) > 0
        else:
            return self.getFieldText().isnumeric()
    

    def validate_and_change_style(self):
        if self.validate_data():
            self.make_normal_style()
            return True
        else:
            self.make_error_style()
            raise ValueError(f"Incorrect value in field \'{self.field_label}\'")