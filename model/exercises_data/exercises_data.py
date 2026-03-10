from pathlib import Path
import json


class ExercisesData:

    def __init__(
            self,
            exercises_file_dir: Path,
            exercises_images_dir: Path
            ):
        with open(exercises_file_dir, 'r') as json_file:
            self.__exercises_dict = json.load(json_file)
        
        self.__exercises_images_dir = exercises_images_dir

    def __len__(self):
        return len(self.__exercises_dict)

    def get_exercise_name(self, idx: int):
        return self.__exercises_dict[idx]

    def get_exercise_image_dir(self, idx: int):
        return self.__exercises_images_dir / f'{idx}.png'