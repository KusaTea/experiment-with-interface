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
- `emg` - data arrays
- `timestamps`

#### Position group keys:
- `imu` - raw data from sensors
- `bones` - quaternions of separated fingers bones
- `fingers` - quaternions of separated fingers
- `timestamps`

#### Markup group keys:
- `exercises`
- `timestamps`