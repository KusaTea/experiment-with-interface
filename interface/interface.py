from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from .modules.stacked_windows import StackedWindows
from .modules.arguments_types import StackedWindowsArgumentsType


class ExperimentInterface(QApplication):

    def __init__(self, arguments, stacked_windows_arguments: StackedWindowsArgumentsType):
        super().__init__(arguments)

        self.setFont(QFont('Arial', 18))

        self.window = StackedWindows(stacked_windows_arguments)
        self.window.setWindowTitle('EMGperiment')
        self.window.show()