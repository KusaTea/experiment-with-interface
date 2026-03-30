import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from controller import Controller
from interface.modules.arguments_types import PatientInfoOptionsType

current_dir = Path()
settings_dir = current_dir / 'settings.json'
exercises_dir = current_dir / 'exercises.json'
exercises_images_dir = current_dir / 'images' / 'hands_gestures'

patient_info_options: PatientInfoOptionsType = {
    'gender_options': ['мужской', 'женский'],
    'hand_options': ['правая', 'левая']
}

if __name__=='__main__':
    app = QApplication()
    app.setFont(QFont('Arial', 18))

    controller = Controller(
        settings_dir=settings_dir,
        patient_info_options=patient_info_options,
        exercises_file_dir=exercises_dir,
        exercises_images_dir=exercises_images_dir
    )

    try:
        controller.stacked_windows.show()
        sys.exit(app.exec())
    
    except BaseException as e:
        app.closeAllWindows()
        app.exit()
        raise e