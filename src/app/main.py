import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt

from controller import Controller


def set_dark_theme(app):
    app.setStyle("Fusion")

    dark_palette = QPalette()

    dark_color = QColor(45, 45, 45)
    disabled_color = QColor(127, 127, 127)
    text_color = QColor(220, 220, 220)

    dark_palette.setColor(QPalette.Window, dark_color)
    dark_palette.setColor(QPalette.WindowText, text_color)

    dark_palette.setColor(QPalette.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.AlternateBase, dark_color)

    dark_palette.setColor(QPalette.ToolTipBase, text_color)
    dark_palette.setColor(QPalette.ToolTipText, text_color)

    dark_palette.setColor(QPalette.Text, text_color)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)

    dark_palette.setColor(QPalette.Button, dark_color)
    dark_palette.setColor(QPalette.ButtonText, text_color)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)

    dark_palette.setColor(QPalette.BrightText, Qt.red)

    dark_palette.setColor(QPalette.Highlight, QColor(90, 130, 200))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)

    app.setPalette(dark_palette)



if __name__=='__main__':
    app = QApplication()
    set_dark_theme(app)
    app.setFont(QFont('Arial', 18))

    controller = Controller()

    try:
        controller.stacked_windows.show()
        sys.exit(app.exec())
    
    except BaseException as e:
        app.closeAllWindows()
        app.exit()
        raise e