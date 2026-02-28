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
    """
    Raw 3-axis accelerometer readings from the MPU6050.

    TimescaleDB hypertable partitioned by time. Written in batches
    by MPU6050Collector at ~75 Hz during an active session.

    Columns:
        time:          UTC timestamp of the reading (composite PK with session_id).
        session_id:    Foreign key → test_sessions.session_id.
        x:             Acceleration on the X axis in m/s².
        y:             Acceleration on the Y axis in m/s².
        z:             Acceleration on the Z axis in m/s².
        quality_score: Optional signal quality indicator.
        is_valid:      False if the reading was flagged as an artefact.
    """
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
        """String representation for logging and debugging."""
        return f"<Accelerometer(time={self.time}, x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})>"


class SensorGyroscope(Base):
    """
    Raw 3-axis gyroscope readings from the MPU6050.

    TimescaleDB hypertable partitioned by time. Written in batches
    by MPU6050Collector alongside accelerometer data at ~75 Hz.

    Columns:
        time:          UTC timestamp of the reading (composite PK with session_id).
        session_id:    Foreign key → test_sessions.session_id.
        x:             Angular velocity on the X axis in deg/s.
        y:             Angular velocity on the Y axis in deg/s.
        z:             Angular velocity on the Z axis in deg/s.
        quality_score: Optional signal quality indicator.
        is_valid:      False if the reading was flagged as an artefact.
    """
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
        """String representation for logging and debugging."""
        return f"<Gyroscope(time={self.time}, x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})>"


class SensorEEG(Base):
    """
    Raw 4-channel EEG readings from the OpenBCI Ganglion via BrainFlow.

    TimescaleDB hypertable partitioned by time. Written in batches
    by EEGCollector at ~46 Hz per channel.

    Columns:
        time:          UTC timestamp of the reading (composite PK with session_id).
        session_id:    Foreign key → test_sessions.session_id.
        channel_1:     EEG channel 1 signal in µV.
        channel_2:     EEG channel 2 signal in µV.
        channel_3:     EEG channel 3 signal in µV.
        channel_4:     EEG channel 4 signal in µV.
        quality_flag:  Integer quality indicator from BrainFlow.
        is_valid:      False if the reading was flagged as an artefact.
    """
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
        """String representation for logging and debugging."""
        return f"<EEG(time={self.time}, ch1={self.channel_1:.2f}, ch2={self.channel_2:.2f})>"


class SensorEyeTracking(Base):
    """
    Gaze position readings from the ArduCam Pinsight AI via MediaPipe.

    TimescaleDB hypertable partitioned by time. Written in batches by
    GazeSystem._collection_loop() after calibration coefficients have
    been applied to map iris position to screen coordinates.

    Columns:
        time:       UTC timestamp of the reading (composite PK with session_id).
        session_id: Foreign key → test_sessions.session_id.
        gaze_x:     Predicted gaze X coordinate in pixels (0 = left edge).
        gaze_y:     Predicted gaze Y coordinate in pixels (0 = top edge).
        raw_yaw:    Optional raw yaw angle in degrees before mapping.
        raw_pitch:  Optional raw pitch angle in degrees before mapping.
        confidence: MediaPipe tracking confidence score (0–1).
        is_valid:   False if no face landmarks were detected in this frame.
    """
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
        """String representation for logging and debugging."""
        return f"<EyeTracking(time={self.time}, gaze=({self.gaze_x:.1f}px, {self.gaze_y:.1f}px))>"


class SensorHeartRate(Base):
    """
    Raw PPG signal readings from the MAX30102.

    TimescaleDB hypertable partitioned by time. Written in batches
    by MAX30102Collector at ~84 Hz during an active session.

    Columns:
        time:       UTC timestamp of the reading (composite PK with session_id).
        session_id: Foreign key → test_sessions.session_id.
        raw_signal: Raw red LED PPG signal value (arbitrary units).
        quality:    Optional signal quality indicator.
        is_valid:   False if the reading was flagged as an artefact.
    """
    __tablename__ = 'sensor_heart_rate'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    raw_signal = Column(Float, nullable=False)
    quality = Column(Integer)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        """String representation for logging and debugging."""
        return f"<HeartRate(time={self.time}, signal={self.raw_signal:.2f})>"


class SensorOximeter(Base):
    """
    Raw red and infrared LED readings from the MAX30102.

    TimescaleDB hypertable partitioned by time. Written alongside
    SensorHeartRate by MAX30102Collector. The infrared signal is
    used for SpO2 calculation in post-processing.

    Columns:
        time:             UTC timestamp of the reading (composite PK with session_id).
        session_id:       Foreign key → test_sessions.session_id.
        red_signal:       Raw red LED signal value (arbitrary units).
        infrared_signal:  Raw infrared LED signal value (arbitrary units).
        is_valid:         False if the reading was flagged as an artefact.
    """
    __tablename__ = 'sensor_oximeter'

    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    red_signal = Column(Float, nullable=False)
    infrared_signal = Column(Float, nullable=False)
    is_valid = Column(Boolean, default=True)

    def __repr__(self):
        """String representation for logging and debugging."""
        return f"<Oximeter(time={self.time}, red={self.red_signal:.2f}, ir={self.infrared_signal:.2f})>"


# ============================================================================
# CALIBRATION DATA MODELS
# ============================================================================

class CalibrationEyeTracking(Base):
    """
    Stores the polynomial regression model fitted during eye tracking calibration.

    One row per session, written by GazeSystem._save_calibration() and
    updated with validation metrics by GazeSystem._save_validation().
    Loaded by SensorPipeline._init_eye_tracking() at sensor startup to
    reconstruct the gaze prediction model without re-running calibration.

    Columns:
        calibration_id:      Primary key, auto-generated UUID.
        session_id:          Foreign key → test_sessions.session_id (unique per session).
        timestamp:           UTC timestamp when calibration was performed.
        coeff_x:             JSONB list of Ridge regression coefficients for X axis.
        coeff_y:             JSONB list of Ridge regression coefficients for Y axis.
        intercept_x:         Ridge regression intercept for X axis.
        intercept_y:         Ridge regression intercept for Y axis.
        poly_degree:         Degree of the PolynomialFeatures transform (default 2).
        calib_features:      JSONB list of raw iris feature vectors for each calibration point.
        calib_targets:       JSONB list of target screen coordinates for each calibration point.
        validation_mean_deg: Mean gaze error across validation points in degrees.
        validation_std_deg:  Std deviation of gaze error in degrees.
        validation_rating:   Summary rating: 'GOOD' (<1.0°), 'ACCEPTABLE' (<2.0°), or 'POOR'.
        notes:               Optional free-text.
    """
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

    # Validation results (filled in after _run_validation)
    validation_mean_deg = Column(Float)   # mean gaze error in degrees
    validation_std_deg  = Column(Float)   # std of gaze error in degrees
    validation_rating   = Column(String)  # 'GOOD', 'ACCEPTABLE', or 'POOR'

    # Metadata
    notes = Column(String)

    def __repr__(self):
        """String representation for logging and debugging."""
        return f"<CalibrationEyeTracking(session_id={self.session_id}, rating={self.validation_rating}, timestamp={self.timestamp})>"

# ============================================================================
# PROCESSED METRICS
# ============================================================================

class MetricsProcessed(Base):
    """
    Derived metrics computed from raw sensor data in post-processing.

    TimescaleDB hypertable partitioned by time. Stores computed values
    such as tremor frequency, heart rate BPM, or SpO2 percentage
    alongside the method used to compute them.

    Columns:
        time:               UTC timestamp of the metric (composite PK with session_id and metric_type).
        session_id:         Foreign key → test_sessions.session_id.
        metric_type:        Identifier for the metric e.g. 'tremor_hz', 'heart_rate_bpm', 'spo2_percent'.
        value:              Computed metric value.
        confidence:         Optional confidence score for the computed value.
        computation_method: Description of the algorithm used to derive the metric.
        is_valid:           False if the computation was flagged as unreliable.
    """
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
        """String representation for logging and debugging."""
        return f"<Metric(type='{self.metric_type}', value={self.value:.2f}, time={self.time})>"
        
