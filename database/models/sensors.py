"""
HERO System - Sensor Data Models
All sensor hypertables and processed metrics
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

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
    """Eye tracking sensor data - 2D screen coordinates and angular data"""
    __tablename__ = 'sensor_eye_tracking'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    gaze_x = Column(Float, nullable=False)  # Screen X coordinate in pixels (0 = left)
    gaze_y = Column(Float, nullable=False)  # Screen Y coordinate in pixels (0 = top)
    raw_yaw = Column(Float)                 # Raw yaw angle in degrees
    raw_pitch = Column(Float)               # Raw pitch angle in degrees
    confidence = Column(Float)              # Tracking confidence (0-1)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        return f"<EyeTracking(time={self.time}, gaze=({self.gaze_x:.1f}px, {self.gaze_y:.1f}px))>"


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
# CALIBRATION DATA MODELS
# ============================================================================

class CalibrationEyeTracking(Base):
    """Eye tracking calibration data — polynomial regression coefficients"""
    __tablename__ = 'calibration_eye_tracking'

    calibration_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'),
                        nullable=False, unique=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Polynomial regression coefficients (15 terms for degree-2 on 4 features)
    coeff_x = Column(JSONB, nullable=False)       # model_x.coef_ as list
    coeff_y = Column(JSONB, nullable=False)       # model_y.coef_ as list
    intercept_x = Column(Float, nullable=False)   # model_x.intercept_
    intercept_y = Column(Float, nullable=False)   # model_y.intercept_
    poly_degree = Column(Integer, nullable=False, default=2)

    # Raw calibration data (for reproducibility / refit)
    calib_features = Column(JSONB)  # list of 9 x [lx, ly, rx, ry]
    calib_targets  = Column(JSONB)  # list of 9 x [tx, ty] in pixels

    # Metadata
    notes = Column(String)

    def __repr__(self):
        return f"<CalibrationEyeTracking(session_id={self.session_id}, timestamp={self.timestamp})>"

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
        
