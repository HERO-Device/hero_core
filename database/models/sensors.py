"""
HERO System - Sensor Data Models
All sensor hypertables and processed metrics
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


# ============================================================================
# RAW SENSOR DATA MODELS
# ============================================================================

class SensorAccelerometer(Base):
    """Accelerometer sensor data - 3-axis acceleration"""
    __tablename__ = 'sensor_accelerometer'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    quality_score = Column(Float)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Accelerometer(time={self.time}, x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})>"


class SensorGyroscope(Base):
    """Gyroscope sensor data - 3-axis rotation"""
    __tablename__ = 'sensor_gyroscope'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    z = Column(Float, nullable=False)
    quality_score = Column(Float)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Gyroscope(time={self.time}, x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})>"


class SensorEEG(Base):
    """EEG sensor data - 4 channels"""
    __tablename__ = 'sensor_eeg'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    channel_1 = Column(Float, nullable=False)
    channel_2 = Column(Float, nullable=False)
    channel_3 = Column(Float, nullable=False)
    channel_4 = Column(Float, nullable=False)
    quality_flag = Column(Integer)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        return f"<EEG(time={self.time}, ch1={self.channel_1:.2f}, ch2={self.channel_2:.2f})>"


class SensorEyeTracking(Base):
    """Eye tracking sensor data - 2D screen coordinates and pupil diameter"""
    __tablename__ = 'sensor_eye_tracking'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    gaze_x = Column(Float)  # Screen X coordinate in pixels (0 = left)
    gaze_y = Column(Float)  # Screen Y coordinate in pixels (0 = top)
    pupil_diameter_left = Column(Float)  # Left pupil diameter (mm)
    pupil_diameter_right = Column(Float)  # Right pupil diameter (mm)
    confidence = Column(Float)  # Tracking confidence (0-1)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        return f"<EyeTracking(time={self.time}, gaze=({self.gaze_x:.1f}px, {self.gaze_y:.1f}px), confidence={self.confidence:.2f})>"


class SensorHeartRate(Base):
    """Heart rate sensor data - raw PPG signal"""
    __tablename__ = 'sensor_heart_rate'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    raw_signal = Column(Float, nullable=False)
    quality = Column(Integer)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        return f"<HeartRate(time={self.time}, signal={self.raw_signal:.2f})>"


class SensorOximeter(Base):
    """Pulse oximeter sensor data - red and infrared signals"""
    __tablename__ = 'sensor_oximeter'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    red_signal = Column(Float, nullable=False)
    infrared_signal = Column(Float, nullable=False)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Oximeter(time={self.time}, red={self.red_signal:.2f}, ir={self.infrared_signal:.2f})>"


# ============================================================================
# PROCESSED METRICS
# ============================================================================

class MetricsProcessed(Base):
    """Processed metrics derived from raw sensor data"""
    __tablename__ = 'metrics_processed'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)
    metric_type = Column(String, nullable=False, primary_key=True)

    value = Column(Float, nullable=False)
    confidence = Column(Float)
    computation_method = Column(String)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Metric(type='{self.metric_type}', value={self.value:.2f}, time={self.time})>"
