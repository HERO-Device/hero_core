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
        return f"<Calibration(sensor='{self.sensor_type}', status='{self.sensor_status}', rate={self.sampling_rate_hz}Hz)>"
