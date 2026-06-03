# GUI for experiment

This project creates GUI for database creation experiment. Database contains high-density sEMG and hand position described by quaternions.

## Features

- Real-time high-density sEMG and 3D hand position synchronous data acquisition

## Technologies

- Python
- PySide6
- NumPy
- h5py

## System requiremets

Windows 10/11

## Installation

1. Download and install SensoGlove DK3 software ([link](https://files.senso.me/install/))
2. Install python packages:
```bash
pip install -r requirements.txt
```

## Run

```bash
python -m app.main
```