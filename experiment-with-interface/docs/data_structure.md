### Database structure description

#### An HDF5 file contains the following attributes:
- `participant_code`
- `participant_age`
- `participant_gender`
- `participant_leading_hand`
- `date`

#### File's groups:
- `emg` - EMG data arrays
- `position` - data from the glove
- `markup` - arrays with numbers of gestures

#### EMG group keys:
- `mV_constant` - attribute that contains constant: each value of emg signal must be multiplied by this constant
- `emg` - emg signal 3D array with shape (length_of_record_in_seconds, sampling_rate, num_of_channels) (default values for sampling_rate and num_of_channels are 10240 and 216 respectively)
- `timestamps` - array of timestamps

#### Position group keys:
- `imu` - 3D array with raw data from imu sensors (samples, imu_sensors, sensor_values).
    Indeces of sensors and their meaning:

    0. palm sensor;
    1. wrist sensor
    2. first thumb sensor
    3. index finger sensor
    4. middle finger sensor
    5. ring finger sensor
    6. little finger sensor
    7. second thumb sensor
    8. empty row

    Indeces of sensors values and their meaning:

    0. state
    1. gyroscope X
    2. gyroscope Y
    3. gyroscope Z
    4. state
    5. accelerometer X
    6. accelerometer Y
    7. accelerometer Z

- `bones` - quaternions of separated fingers bones:

    0. Palm
    1. Thumb proximal phalanx
    2. Thumb distal phalanx
    3. Thumb tip segment
    4. Index proximal phalanx
    5. Index middle phalanx
    6. Index distal phalanx
    7. Middle proximal phalanx
    8. Middle middle phalanx
    9. Middle distal phalanx
    10. Ring proximal phalanx
    11. Ring middle phalanx
    12. Ring distal phalanx
    13. Little proximal phalanx
    14. Little middle phalanx
    15. Little distal phalanx

- `fingers` - quaternions of separated fingers:

    0. thumb (first sensor)
    1. thumb (second sensor)
    2. index finger
    3. middle finger
    4. ring finger
    5. little finger

- `timestamps`

#### Markup group keys:
- `exercises`- numbers of the beginning and the end of exercises
- `timestamps`