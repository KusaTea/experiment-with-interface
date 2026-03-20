from typing import Callable, Literal, Tuple

from PySide6.QtWidgets import QWidget, QHBoxLayout

from ..elements import TextField, RadioButtons, VerticalLayout, SecondaryButton
from ..arguments_types import PatientInfoOptionsType


class PatientInfoWindow(QWidget):

    def __init__(
            self,
            patient_info_options: PatientInfoOptionsType
            ):
        super().__init__()

        layout = VerticalLayout()

        self.code_field = TextField(field_hint='введите текст...', label_text='код испытуемого', field_data_type='number')
        layout.addWidget(self.code_field)
        
        self.age_field = TextField(field_hint='введите число...', label_text='возраст', field_data_type='number')
        layout.addWidget(self.age_field)

        self.gender_radio = RadioButtons(options=patient_info_options['gender_options'], label_text='пол')
        layout.addWidget(self.gender_radio)

        self.hand_radio = RadioButtons(options=patient_info_options['hand_options'], label_text='ведущая рука')
        layout.addWidget(self.hand_radio)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(50)

        self.back_button = SecondaryButton('назад')
        buttons_layout.addWidget(self.back_button)

        self.next_button = SecondaryButton('далее')
        buttons_layout.addWidget(self.next_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)


    def validate_text_fields(self):
        is_valid = True
        for field in (self.code_field, self.age_field):
            try:
                field.validate_and_change_style()
            except ValueError:
                is_valid = False
        
        return is_valid


    def add_callback_for_back_button(self, callback: Callable):
        self.back_button.clicked.connect(callback)
    

    def add_callback_for_next_button(self, callback: Callable):
        self.next_button.clicked.connect(callback)


    def get_patient_code(self) -> str:
        return self.code_field.getFieldText()
    

    def get_patient_age(self) -> str:
        return self.age_field.getFieldText()
    

    def get_patient_gender(self) -> Literal['мужской', 'женский']:
        return self.gender_radio.get_selected_option()
        

    def get_patient_hand(self) -> Literal['левая', 'правая']:
        return self.hand_radio.get_selected_option()


    def get_patient_info(self) -> Tuple[str, str, Literal['мужской', 'женский'], Literal['левая', 'правая']]:
        if self.validate_text_fields():
            return (
                self.get_patient_code(),
                self.get_patient_age(),
                self.get_patient_gender(),
                self.get_patient_hand()
            )
        
        else:
            raise ValueError('Fields contain incorrect values')
    
    
    def reset(self):
        self.code_field.reset()
        self.age_field.reset()
        self.gender_radio.reset()
        self.hand_radio.reset()