from PySide6.QtCore import QObject, Signal


class MainWindowController(QObject):

    finished = Signal()
    new_record_button_pushed = Signal()
    settings_button_pushed = Signal()
    
    def __init__(self, window, stop_signal: Signal):

        super().__init__()

        self.__main_window = window
        self.__main_window.add_callback_for_new_record_button(self.__new_record_callback)
        self.__main_window.add_callback_for_settings_button(self.__settings_callback)
        
        stop_signal.connect(self.__finish)
    

    def __new_record_callback(self):
        self.new_record_button_pushed.emit()
    

    def __settings_callback(self):
        self.settings_button_pushed.emit()
    

    def __finish(self):
        self.finished.emit()

    