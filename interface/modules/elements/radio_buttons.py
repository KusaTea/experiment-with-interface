from PySide6.QtWidgets import QWidget, QLabel, QRadioButton, QGroupBox, QVBoxLayout

from typing import List

_style = '''

'''

class RadioButtons(QWidget):

    def __init__(self, options: List[str], label_text: str = ''):
        super().__init__()

        self.setStyleSheet(_style)

        layout = QVBoxLayout()

        layout.setSpacing(5)

        layout.addWidget(QLabel(label_text))

        group_layout = QVBoxLayout()
        self.buttons: List[QRadioButton] = list()
        for option in options:
            button = QRadioButton(option)
            self.buttons.append(button)
            group_layout.addWidget(button)
        self.buttons[0].setChecked(True)

        buttons_group = QGroupBox(flat=True)
        buttons_group.setLayout(group_layout)

        layout.addWidget(buttons_group)

        self.setLayout(layout)
    

    def get_selected_option(self) -> str:
        button_text = ''
        for button in self.buttons:
            if button.isChecked():
                button_text = button.text()
        
        return button_text