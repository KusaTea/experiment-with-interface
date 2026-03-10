import json
from pathlib import Path


class SettingsData:

    def __init__(self, settings_dir: Path):

        with open(settings_dir, 'r') as json_file:
            self.__settings = json.load(json_file)
    
    def __getitem__(self, key: str):
        return self.__settings[key]

    @property
    def settings(self):
        return self.__settings