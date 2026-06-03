from pathlib import Path

class DirsStore:

    def __init__(
        self,
        data_main_dir: Path,
        exercises_dir: Path,
        exercises_images_dir: Path,
        background_image_dir: Path
        ):
        
        self.__data_main_dir = data_main_dir
        self.__exercises_dir = exercises_dir
        self.__exercises_images_dir = exercises_images_dir
        self.__background_image_dir = background_image_dir
        self.__raw_data_dir = None
        self.__ready_data_dir = None


    @property
    def data_main_dir(self) -> Path:
        return self.__data_main_dir


    @data_main_dir.setter
    def data_main_dir(self, dr: Path):
        assert isinstance(dr, Path)
        self.__data_main_dir = dr
    

    @property
    def raw_data_dir(self) -> Path:
        return self.__raw_data_dir


    @raw_data_dir.setter
    def raw_data_dir(self, dr: Path):
        assert isinstance(dr, Path)
        self.__raw_data_dir = dr


    @property
    def ready_data_dir(self) -> Path:
        return self.__ready_data_dir


    @ready_data_dir.setter
    def ready_data_dir(self, dr: Path):
        assert isinstance(dr, Path)
        self.__ready_data_dir = dr
    

    @property
    def exercises_dir(self) -> Path:
        return self.__exercises_dir


    @exercises_dir.setter
    def exercises_dir(self, dr: Path):
        assert isinstance(dr, Path)
        self.__exercises_dir = dr

    
    @property
    def exercises_images_dir(self) -> Path:
        return self.__exercises_images_dir


    @exercises_images_dir.setter
    def exercises_images_dir(self, dr: Path):
        assert isinstance(dr, Path)
        self.__exercises_images_dir = dr

    
    @property
    def background_image_dir(self) -> Path:
        return self.__background_image_dir


    @background_image_dir.setter
    def background_image_dir(self, dr: Path):
        assert isinstance(dr, Path)
        self.__background_image_dir = dr