from interface.modules.stacked_windows import StackedWindows


class MainWindowController:
    
    def __init__(self, stacked_windows: StackedWindows):
        self.__stacked_windows: StackedWindows = stacked_windows
        main_window = stacked_windows.main_window

        main_window.add_callback_for_new_record_button(self.__new_record_callback)
        main_window.add_callback_for_settings_button(self.__settings_callback)
    

    def __new_record_callback(self):
        self.__stacked_windows.display_patient_info()
    

    def __settings_callback(self):
        self.__stacked_windows.display_settings()

    