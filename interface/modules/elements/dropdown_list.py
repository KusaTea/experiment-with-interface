from typing import List

from PySide6.QtWidgets import QWidget, QComboBox, QLabel, QVBoxLayout

from ..constants import constants

_style = '''
QComboBox {{
    padding: 5px;
    border: solid 1px {border_color};
    border-radius: 10px;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border: none;
    border-top-right-radius: 10px; 
    border-bottom-right-radius: 10px;
}}
'''.format(
    border_color=constants.border_color
)

class DropdownList(QWidget):

    def __init__(self, dropdown_items: List[str], label_text: str = ''):
        super().__init__()

        self.setStyleSheet(_style)

        layout = QVBoxLayout()

        layout.setSpacing(5)

        self.label = QLabel(label_text)
        layout.addWidget(self.label)
        self.dropdown = QComboBox()
        self.dropdown.addItems(dropdown_items)
        layout.addWidget(self.dropdown)

        self.setLayout(layout)
    
    def set_current_option_by_index(self, index: int):
        self.dropdown.setCurrentIndex(index)
    
    def get_current_option_index(self) -> int:
        return self.dropdown.currentIndex()
    
    def get_current_option(self) -> str:
        return self.dropdown.currentText()