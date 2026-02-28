"""
HERO System - Sensor Calibration Model
Sensor configuration and status metadata
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base


class SensorCalibration(Base):
    """Sensor calibration and configuration metadata"""
    """
    Records sensor calibration and configuration metadata for a session.

    Written by SensorPipeline._log_sensor_status() for both successful and
    failed sensor initialisations, so every session has a complete audit
    trail of which hardware was active.

    Columns:
        calibration_id:        Primary key, auto-generated UUID.
        session_id:            Foreign key → test_sessions.session_id.
        sensor_type:           Sensor identifier: 'mpu6050', 'max30102', 'eeg', 'eye_tracking'.
        sampling_rate_hz:      Actual sampling rate achieved. None if sensor failed.
        calibration_timestamp: UTC timestamp when this record was written.
        calibration_params:    JSONB dict of sensor-specific config (I2C address, ranges, mode, etc.).
        sensor_status:         One of: 'active', 'failed', 'disconnected', 'recovered'.
        hardware_version:      Optional hardware version string.
        firmware_version:      Optional firmware version string.
        notes:                 Free-text, typically the exception message on failure.

    Relationships:
        session: Many-to-one → TestSession.
    """
    __tablename__ = 'sensor_calibration'

    calibration_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False)

    sensor_type = Column(String, nullable=False)
    sampling_rate_hz = Column(Integer)
    calibration_timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    calibration_params = Column(JSONB)
    sensor_status = Column(String)  # 'active', 'failed', 'disconnected', 'recovered'
    hardware_version = Column(String)
    firmware_version = Column(String)
    notes = Column(Text)

    # Relationships
    session = relationship("TestSession", back_populates="calibrations")

    def __repr__(self):
        """String representation for logging and debugging."""
        return f"<Calibration(sensor='{self.sensor_type}', status='{self.sensor_status}', rate={self.sampling_rate_hz}Hz)>"
