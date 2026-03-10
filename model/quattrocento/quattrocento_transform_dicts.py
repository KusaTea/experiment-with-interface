sampling_rate_transform_dict = {
    512: 0,
    2048: 8,
    5120: 16,
    10240: 24
    }

analog_output_gain_transform_dict = {
    1: 0,
    2: 16,
    4: 32,
    16: 48
    }

side_transform_dict = {
    "left": 64,
    "right": 128,
    None: 0,
    "not defined": 192
    }

high_pass_filter_threshold_transform_dict = {
    0.3: 0,
    10: 16,
    100: 32,
    200: 48
    }

low_pass_filter_threshold_transform_dict = {
    130: 0,
    500: 4,
    900: 8,
    4400: 12
    }

lead_mode_transform_dict = {
    "monopolar": 0,
    "differential": 1,
    "bipolar": 2
    }