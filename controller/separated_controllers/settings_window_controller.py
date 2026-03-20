from interface.modules.stacked_windows import StackedWindows


class SettingsWindowController:
    
    def __init__(self, stacked_windows: StackedWindows):
        self.__stacked_windows = stacked_windows
        
        settings_window = self.__stacked_windows.settings_window
        settings_window.add_callback_for_back_button(self.__back_callback)
        settings_window.add_callback_for_save_button(self.__save_callback)

    
    def __back_callback(self):
        self.__stacked_windows.display_main_menu()
        # TODO: finish function

    
    def __save_callback(self):
        self.__stacked_windows.display_main_menu()
        # TODO: finish function