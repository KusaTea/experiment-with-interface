from pathlib import Path
import json


class LabelsData:
    
    def __init__(self, labels_dir: Path, lang: str):

        self.__labels_dir = labels_dir
        self.__load_labels(lang)
        
    
    def __getitem__(self, key: str):
        return self.__labels[key]
    

    def __load_labels(self, lang):
        with open(self.__labels_dir, mode='r') as json_file:
            self.__labels = json.load(json_file)[lang]