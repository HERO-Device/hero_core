-- ============================================================================
-- HERO System - Sensor Data Schema
-- ============================================================================
-- Description: Time-series sensor data collection and processed metrics
-- Requires: TimescaleDB extension
-- Version: 1.0.0
-- ============================================================================

-- Enable TimescaleDB extension
-- CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- RAW SENSOR DATA - ACCELEROMETER
-- ============================================================================
-- 3-axis acceleration data for tremor detection
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensor_accelerometer (
    time TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    x DOUBLE PRECISION NOT NULL,  -- X-axis acceleration (m/s²)
    y DOUBLE PRECISION NOT NULL,  -- Y-axis acceleration (m/s²)
    z DOUBLE PRECISION NOT NULL,  -- Z-axis acceleration (m/s²)
    quality_score DOUBLE PRECISION,  -- 0-1 scale for data quality
    is_valid BOOLEAN DEFAULT TRUE
);

-- Convert to hypertable (time-series optimized)
-- SELECT create_hypertable('sensor_accelerometer', 'time', if_not_exists => TRUE);

-- Create index on session_id for querying specific sessions
CREATE INDEX idx_accel_session ON sensor_accelerometer(session_id, time DESC);

COMMENT ON TABLE sensor_accelerometer IS '3-axis accelerometer data for motion and tremor detection';

-- ============================================================================
-- RAW SENSOR DATA - GYROSCOPE
-- ============================================================================
-- 3-axis rotational data
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensor_gyroscope (
    time TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    x DOUBLE PRECISION NOT NULL,  -- X-axis rotation (rad/s or deg/s)
    y DOUBLE PRECISION NOT NULL,  -- Y-axis rotation
    z DOUBLE PRECISION NOT NULL,  -- Z-axis rotation
    quality_score DOUBLE PRECISION,
    is_valid BOOLEAN DEFAULT TRUE
);

-- SELECT create_hypertable('sensor_gyroscope', 'time', if_not_exists => TRUE);
CREATE INDEX idx_gyro_session ON sensor_gyroscope(session_id, time DESC);

COMMENT ON TABLE sensor_gyroscope IS '3-axis gyroscope data for rotational motion detection';

-- ============================================================================
-- RAW SENSOR DATA - EEG (4 CHANNELS)
-- ============================================================================
-- EEG signals from 4 channels
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensor_eeg (
    time TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    channel_1 DOUBLE PRECISION NOT NULL,  -- EEG channel 1 (µV)
    channel_2 DOUBLE PRECISION NOT NULL,  -- EEG channel 2 (µV)
    channel_3 DOUBLE PRECISION NOT NULL,  -- EEG channel 3 (µV)
    channel_4 DOUBLE PRECISION NOT NULL,  -- EEG channel 4 (µV)
    quality_flag INTEGER,  -- Quality indicator (e.g., 0=good, 1=artifact, 2=noise)
    is_valid BOOLEAN DEFAULT TRUE
);

-- SELECT create_hypertable('sensor_eeg', 'time', if_not_exists => TRUE);
CREATE INDEX idx_eeg_session ON sensor_eeg(session_id, time DESC);

COMMENT ON TABLE sensor_eeg IS '4-channel EEG data for brain activity monitoring';
COMMENT ON COLUMN sensor_eeg.quality_flag IS '0=good, 1=artifact, 2=noise, 3=electrode disconnected';

-- ============================================================================
-- RAW SENSOR DATA - EYE TRACKING
-- ============================================================================
-- Gaze position and pupil diameter
-- NOTE: Schema may need refinement after eye tracking demo from team
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensor_eye_tracking (
    time TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    gaze_x DOUBLE PRECISION,  -- Gaze X coordinate (screen coordinates or normalized)
    gaze_y DOUBLE PRECISION,  -- Gaze Y coordinate
    pupil_diameter_left DOUBLE PRECISION,   -- Left pupil diameter (mm)
    pupil_diameter_right DOUBLE PRECISION,  -- Right pupil diameter (mm)
    confidence DOUBLE PRECISION,  -- Tracking confidence (0-1)
    is_valid BOOLEAN DEFAULT TRUE
);

-- SELECT create_hypertable('sensor_eye_tracking', 'time', if_not_exists => TRUE);
CREATE INDEX idx_eye_session ON sensor_eye_tracking(session_id, time DESC);

COMMENT ON TABLE sensor_eye_tracking IS 'Eye tracking data: gaze position and pupil diameter (schema subject to revision)';
COMMENT ON COLUMN sensor_eye_tracking.confidence IS 'Tracking confidence score (0-1), low values indicate tracking loss';

-- ============================================================================
-- RAW SENSOR DATA - HEART RATE (PPG)
-- ============================================================================
-- Raw photoplethysmography signal
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensor_heart_rate (
    time TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    raw_signal DOUBLE PRECISION NOT NULL,  -- Raw PPG signal value
    quality INTEGER,  -- Signal quality (0=poor, 1=fair, 2=good)
    is_valid BOOLEAN DEFAULT TRUE
);

-- SELECT create_hypertable('sensor_heart_rate', 'time', if_not_exists => TRUE);
CREATE INDEX idx_hr_session ON sensor_heart_rate(session_id, time DESC);

COMMENT ON TABLE sensor_heart_rate IS 'Raw PPG (photoplethysmography) signal for heart rate detection';

-- ============================================================================
-- RAW SENSOR DATA - PULSE OXIMETER
-- ============================================================================
-- Raw red and infrared signals for SpO2 calculation
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensor_oximeter (
    time TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    red_signal DOUBLE PRECISION NOT NULL,      -- Red LED signal
    infrared_signal DOUBLE PRECISION NOT NULL,  -- Infrared LED signal
    is_valid BOOLEAN DEFAULT TRUE
);

-- SELECT create_hypertable('sensor_oximeter', 'time', if_not_exists => TRUE);
CREATE INDEX idx_oximeter_session ON sensor_oximeter(session_id, time DESC);

COMMENT ON TABLE sensor_oximeter IS 'Raw red and infrared signals for blood oxygen saturation (SpO2) calculation';

-- ============================================================================
-- PROCESSED METRICS
-- ============================================================================
-- Computed metrics derived from raw sensor data
-- Lower frequency than raw data (~1 Hz or computed on-demand)
-- ============================================================================

CREATE TABLE IF NOT EXISTS metrics_processed (
    time TIMESTAMPTZ NOT NULL,
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL,  -- e.g., 'heart_rate_bpm', 'spo2_percent', 'tremor_amplitude'
    value DOUBLE PRECISION NOT NULL,
    confidence DOUBLE PRECISION,  -- Confidence in the computed value (0-1)
    computation_method TEXT,  -- Algorithm/version used for reproducibility
    is_valid BOOLEAN DEFAULT TRUE
);

-- SELECT create_hypertable('metrics_processed', 'time', if_not_exists => TRUE);
CREATE INDEX idx_metrics_session ON metrics_processed(session_id, time DESC);
CREATE INDEX idx_metrics_type ON metrics_processed(metric_type, time DESC);

COMMENT ON TABLE metrics_processed IS 'Processed metrics computed from raw sensor data';
COMMENT ON COLUMN metrics_processed.metric_type IS 'Type of metric: heart_rate_bpm, spo2_percent, tremor_amplitude, tremor_frequency, eeg_alpha_power, etc.';
COMMENT ON COLUMN metrics_processed.computation_method IS 'Algorithm version for reproducibility (e.g., "wavelet_v1.2", "fft_v2.0")';

-- ============================================================================
-- SENSOR CALIBRATION METADATA
-- ============================================================================
-- Records sensor configuration and status for each session
-- Links to quality_score/is_valid fields in sensor tables to explain data quality
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensor_calibration (
    calibration_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    sensor_type TEXT NOT NULL,  -- e.g., 'accelerometer', 'eeg', 'eye_tracking'
    sampling_rate_hz INTEGER,   -- Actual sampling rate achieved
    calibration_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    calibration_params JSONB,   -- Flexible storage for sensor-specific parameters
    sensor_status TEXT,         -- 'active', 'failed', 'disconnected', 'recovered'
    hardware_version TEXT,
    firmware_version TEXT,
    notes TEXT
);

CREATE INDEX idx_calibration_session ON sensor_calibration(session_id);
CREATE INDEX idx_calibration_sensor ON sensor_calibration(sensor_type);

COMMENT ON TABLE sensor_calibration IS 'Sensor configuration and status metadata - use to understand data quality issues';
COMMENT ON COLUMN sensor_calibration.sensor_status IS 'Sensor operational status: active, failed, disconnected, recovered';
COMMENT ON COLUMN sensor_calibration.calibration_params IS 'JSON storage for sensor-specific calibration data (e.g., gains, offsets, ranges)';
COMMENT ON COLUMN sensor_calibration.notes IS 'Human-readable notes about sensor issues or configuration';