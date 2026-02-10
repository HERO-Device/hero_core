"""
HERO Core - Configuration Module
Exposes configuration settings and helper functions
"""

from .config import (
    DATABASE,
    SENSOR_RATES,
    SENSOR_CONFIG,
    QUALITY_THRESHOLDS,
    get_sensor_rate,
    get_sensor_config,
    is_sensor_enabled,
)

__all__ = [
    'DATABASE',
    'SENSOR_RATES',
    'SENSOR_CONFIG',
    'QUALITY_THRESHOLDS',
    'get_sensor_rate',
    'get_sensor_config',
    'is_sensor_enabled',
]