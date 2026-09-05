from view.types import PatientInfoOptionsType


participant_info_options = {
    'rus': {
        'gender_options': ['мужской', 'женский'],
        'hand_options': ['правая', 'левая']
    },
    'eng': {
        'gender_options': ['male', 'female'],
        'hand_options': ['right', 'left']
    }
}


bar_info = {
    'min_value': 0,
    'max_value': 1
    }


myograph_settings_data = {
    'rus': {
        'high_pass_filter_options': [
            '0.3',
            '10',
            '100',
            '200'
            ],
        'low_pass_filter_options': [
            '130',
            '500',
            '900',
            '4400'
            ],
        'detecion_mode_options': [
            'биполярное',
            'монополярное',
            'дифференциальное'
            ],
        'electrodes_type_options': [
            'не определено',
            '16 monopolar EEG',
            'Mon. intram. el.',
            'Bip. el - CoDe',
            '8 Acceleromet.',
            'Bipolar el. - DE1',
            'Bipolar el. - CDE',
            'Bip. el. - other',
            '4 el. Array 10mm',
            '8 el. Array 5mm',
            '8 el. Array 10 mm',
            '64 el. Gr. 2.54mm',
            '64 el. Grid 8mm',
            '64 el. Grid 10 mm',
            '64 el. Gr. 12.5mm',
            '16 el. Array 2.5mm',
            '16 el. Array 5mm',
            '16 el. Array 10mm',
            '16 el. Array 10mm',
            '16 el. retal pr.',
            '48 el. retal pr.',
            '12 el. Aemband.',
            '16 el. Armband',
            'другие'
            ],
        'adapter_type_options': [
            'не определено',
            '16ch AD1x16',
            '8ch AD2x8',
            '4ch AD4x4',
            '64ch AD1x64',
            '16ch AD8x2',
            'другой'
            ]
    },
    'eng': {
            'high_pass_filter_options': [
                '0.3',
                '10',
                '100',
                '200'
                ],
            'low_pass_filter_options': [
                '130',
                '500',
                '900',
                '4400'
                ],
            'detecion_mode_options': [
                'bipolar',
                'monopolar',
                'differential'
                ],
            'electrodes_type_options': [
                'not defined',
                '16 monopolar EEG',
                'Mon. intram. el.',
                'Bip. el - CoDe',
                '8 Acceleromet.',
                'Bipolar el. - DE1',
                'Bipolar el. - CDE',
                'Bip. el. - other',
                '4 el. Array 10mm',
                '8 el. Array 5mm',
                '8 el. Array 10 mm',
                '64 el. Gr. 2.54mm',
                '64 el. Grid 8mm',
                '64 el. Grid 10 mm',
                '64 el. Gr. 12.5mm',
                '16 el. Array 2.5mm',
                '16 el. Array 5mm',
                '16 el. Array 10mm',
                '16 el. Array 10mm',
                '16 el. retal pr.',
                '48 el. retal pr.',
                '12 el. Aemband.',
                '16 el. Armband',
                'other'
                ],
            'adapter_type_options': [
                'not defined',
                '16ch AD1x16',
                '8ch AD2x8',
                '4ch AD4x4',
                '64ch AD1x64',
                '16ch AD8x2',
                'other'
                ]
        }
}