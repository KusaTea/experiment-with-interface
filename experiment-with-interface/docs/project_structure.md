`app` \
├── `config` \
├── `controller` - code that binds interface with data \
│   ├── `main_controller.py` \
│   ├── `modules` \
│   │   ├── `data_converter.py` \
│   │   └── `store.py` - global config store \
│   ├── `separated_controllers` \
│   │   ├── `connection_window_controller.py` \
│   │   ├── `experiment_window_controller.py` \
│   │   ├── `finish_window_controller.py` \
│   │   ├── `main_window_controller.py` \
│   │   ├── `participant_info_window_controller.py` \
│   │   └── `settings_window_controller.py` \
│   └── `types.py` \
├── `data` - code files that manipulates data \
│   ├── `abstracts.py` \
│   ├── `models.py` \
│   ├── `repositories` \
│   │   ├── `data_merger.py` \
│   │   ├── `emg_data_reader.py` \
│   │   ├── `exercises_data.py` \
│   │   ├── `markup_data.py` \
│   │   ├── `participant_data.py` \
│   │   ├── `quattrocento_data_handler.py` \
│   │   ├── `quattrocento_module.py` \
│   │   ├── `quattrocento_settings.py` \
│   │   ├── `raw_glove_data_reader.py` \
│   │   ├── `sensoglove_data_handler.py` \
│   │   ├── `sensoglove_module.py` \
│   │   └── `settings_data.py` \
│   ├── `services` \
│   │   └── `exercises_iterator.py` \
│   └── `types.py` \
├── `main.py` \
├── `resources` - files with custom data: exercises, interface images and settings \
│   ├── `exercises.json` - ids and names of exercises \
│   ├── `images` \
│   │   ├── `backgrounds` - background images \
│   │   └── `hands_gestures` - gestures images \
│   └── `settings.json` - app settings \
├── `scripts` \
│   ├── `merge_data_manually.py` \
│   └── `merge_data_manually_several.py` \
├── `utils` \
│   ├── `dirs_data.py` \
│   └── `view_data.py` \
└── `view` - interface code files \
    ├── `constants.py` \
    ├── `elements` - windows\` elements \
    │   ├── `button.py` \
    │   ├── `dropdown_list.py` \
    │   ├── `label.py` \
    │   ├── `progress_bar.py` \
    │   ├── `radio_buttons.py` \
    │   ├── `text_field.py` \
    │   └── `vertical_layout.py` \
    ├── `main_window.py` - window that aggregates all separated windows \
    ├── `models.py` - dictionaries types \
    ├── `types.py` - arguments types \
    └── `windows` - separated windows \
        ├── `main__window.py` - main menu window \
        ├── `new_record_connection__window.py` - connection to the myograph and the glove window  \
        ├── `new_record_experiment__window.py` - window that displays gestures \
        ├── `new_record_finish__window.py` - experiment finish window \
        ├── `new_record_patient__window.py` - window with participant\`s data \
        └── `settings__window.py` - settings window