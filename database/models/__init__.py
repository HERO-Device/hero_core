# HERO Core - Database Models
# Imports all models so SQLAlchemy can resolve relationships correctly

from .base import Base

# Core tables
# AnonDemographics must be imported before TestSession so SQLAlchemy
# can resolve the anon_demographics relationship on TestSession.
from .anon_demographics import AnonDemographics
from .user import User
from .session import TestSession

# Sensor calibration (must come before sensors due to relationships)
from .calibration import SensorCalibration

# Sensor data
from .sensors import (
    SensorAccelerometer,
    SensorGyroscope,
    SensorEEG,
    SensorEyeTracking,
    SensorHeartRate,
    SensorOximeter,
    CalibrationEyeTracking,
    MetricsProcessed,
)

# Ethics & compliance
from .ethics import (
    UserConsent,
    DataLifecycleLog,
    RetentionPolicy,
)

# Events & game results
from .events import Event
from .game_results import GameResult

# Connection helpers
from .connection import create_db_engine, create_db_session, get_db_connection

__all__ = [
    'Base',
    # Core
    'AnonDemographics',
    'User',
    'TestSession',
    # Calibration
    'SensorCalibration',
    # Sensors
    'SensorAccelerometer',
    'SensorGyroscope',
    'SensorEEG',
    'SensorEyeTracking',
    'SensorHeartRate',
    'SensorOximeter',
    'CalibrationEyeTracking',
    'MetricsProcessed',
    # Ethics
    'UserConsent',
    'DataLifecycleLog',
    'RetentionPolicy',
    # Events & results
    'Event',
    'GameResult',
    # Connection
    'create_db_engine',
    'create_db_session',
    'get_db_connection',
]
