# Import ethics models
from .ethics import (
    UserConsent,
    DataLifecycleLog,
    RetentionPolicy
)

from .game_results import GameResult

# Import events model
from .events import Event

# Update __all__ to include new models
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
    
    # Ethics & Compliance
    'UserConsent',
    'DataLifecycleLog',
    'RetentionPolicy',
    
    # Events
    'Event',
    
    # Connection helpers
    'create_db_engine',
    'create_db_session',
    'get_db_connection',
]
