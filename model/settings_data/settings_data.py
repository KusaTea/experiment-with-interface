import json
from pathlib import Path


class SettingsData:

    def __init__(self, settings_dir: Path):

        self.__settings_dir = settings_dir
        self.__load_settings()
        
    
    def __getitem__(self, key: str):
        return self.__settings[key]


    @property
    def settings(self):
        return self.__settings
    

    def __load_settings(self):
        with open(self.__settings_dir, 'r') as json_file:
            self.__settings = json.load(json_file)
    

    def __save_settings(self):
        with open(self.__settings_dir, 'w') as json_file:
            json.dump(self.__settings, json_file)
    

    def update_settings(self, settings):
        self.__settings = settings
        self.__save_settings()