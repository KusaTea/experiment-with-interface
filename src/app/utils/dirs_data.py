from pathlib import Path
from os import listdir


resources_dir = Path('./app/resources')
settings_dir = resources_dir / 'settings.json'
exercises_dir = resources_dir / 'exercises.json'
exercises_images_dir = resources_dir / 'images' / 'hands_gestures'
background_images_dirs = [(resources_dir / 'images' / 'backgrounds' / file_name) for file_name in listdir(resources_dir / 'images' / 'backgrounds')]