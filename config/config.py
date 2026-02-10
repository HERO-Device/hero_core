"""
HERO Core - Configuration
Simple configuration file for database and sensor settings
"""

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': '',  # Leave empty for interactive prompt
    'dbname': 'hero_db',
}

# ============================================================================
# SENSOR SAMPLING RATES (Hz)
# ============================================================================

SENSOR_RATES = {
    'accelerometer': 100,
    'gyroscope': 100,
    'eeg': 250,
    'eye_tracking': 60,
    'heart_rate': 100,
    'oximeter': 100,
}

# ============================================================================
# SENSOR SETTINGS
# ============================================================================

SENSOR_CONFIG = {
    'accelerometer': {
        'enabled': True,
        'range': '±8g',
        'units': 'm/s²',
    },
    'gyroscope': {
        'enabled': True,
        'range': '±500°/s',
        'units': 'deg/s',
    },
    'eeg': {
        'enabled': True,
        'channels': 4,
        'units': 'µV',
        'power_supply_voltage': 3.3,  # Volts
    },
    'eye_tracking': {
        'enabled': True,
        'units': 'pixels',
        'confidence_threshold': 0.7,
    },
    'heart_rate': {
        'enabled': True,
        'units': 'arbitrary',  # Raw PPG
    },
    'oximeter': {
        'enabled': True,
        'units': 'arbitrary',  # Raw signals
    },
}

# ============================================================================
# DATA QUALITY THRESHOLDS
# ============================================================================

QUALITY_THRESHOLDS = {
    'accelerometer_min': 0.5,
    'gyroscope_min': 0.5,
    'eeg_max_artifact_percent': 30,
    'eye_tracking_min_confidence': 0.6,
    'heart_rate_min_quality': 1,  # 0=poor, 1=fair, 2=good
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sensor_rate(sensor_name):
    """
    Get sampling rate for a sensor

    Args:
        sensor_name: Name of sensor (e.g., 'eeg', 'accelerometer')

    Returns:
        int: Sampling rate in Hz
    """
    return SENSOR_RATES.get(sensor_name)


def get_sensor_config(sensor_name):
    """
    Get configuration for a sensor

    Args:
        sensor_name: Name of sensor

    Returns:
        dict: Sensor configuration
    """
    return SENSOR_CONFIG.get(sensor_name, {})


def is_sensor_enabled(sensor_name):
    """
    Check if a sensor is enabled

    Args:
        sensor_name: Name of sensor

    Returns:
        bool: True if enabled
    """
    config = get_sensor_config(sensor_name)
    return config.get('enabled', False)