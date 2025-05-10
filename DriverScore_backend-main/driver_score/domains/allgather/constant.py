from enum import Enum


class CollectedDataType(str, Enum):
    ACCELERATION = "acceleration"
    CALIBRATION = "calibration"
    LOCATION = "location"
    CAMERA = "camera"


class CalibrationStatus(str, Enum):
    NO_CALIBRATION = "no_calibration"
    IMPROPER_CALIBRATION = "improper_calibration"
    GOOD_CALIBRATION = "good_calibration"


# TODO: Add supported zip format here
