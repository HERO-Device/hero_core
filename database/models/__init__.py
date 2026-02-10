"""
HERO System - Database Models Package
SQLAlchemy ORM models for all database tables
"""

# Import Base first
from .base import Base

# Import all models
from .user import User
from .session import TestSession
from .sensors import (
    SensorAccelerometer,
    SensorGyroscope,
    SensorEEG,
    SensorEyeTracking,
    SensorHeartRate,
    SensorOximeter,
    MetricsProcessed
)
from .calibration import SensorCalibration

# Import connection helpers
from .connection import (
    create_db_engine,
    create_db_session,
    get_db_connection
)

# Export all
__all__ = [
    # Base
    'Base',

    # Core tables
    'User',
    'TestSession',

    # Sensor data
    'SensorAccelerometer',
    'SensorGyroscope',
    'SensorEEG',
    'SensorEyeTracking',
    'SensorHeartRate',
    'SensorOximeter',
    'MetricsProcessed',

    # Metadata
    'SensorCalibration',

    # Connection helpers
    'create_db_engine',
    'create_db_session',
    'get_db_connection',
]
