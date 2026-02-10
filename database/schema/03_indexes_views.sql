-- ============================================================================
-- HERO System - Indexes and Views
-- ============================================================================
-- Description: Performance indexes and convenience views for common queries
-- Version: 1.0.0
-- NOTE: Continuous aggregates commented out for Windows testing (require TimescaleDB)
-- ============================================================================

-- ============================================================================
-- ADDITIONAL PERFORMANCE INDEXES
-- ============================================================================

-- Composite indexes for common time-range queries per session
-- These speed up queries like "get all accelerometer data for session X between time A and B"

CREATE INDEX IF NOT EXISTS idx_accel_session_time
ON sensor_accelerometer(session_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_gyro_session_time
ON sensor_gyroscope(session_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_eeg_session_time
ON sensor_eeg(session_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_eye_session_time
ON sensor_eye_tracking(session_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_hr_session_time
ON sensor_heart_rate(session_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_oximeter_session_time
ON sensor_oximeter(session_id, time DESC);

-- Index for finding invalid/low-quality data
CREATE INDEX IF NOT EXISTS idx_accel_invalid
ON sensor_accelerometer(session_id, time DESC)
WHERE is_valid = FALSE;

CREATE INDEX IF NOT EXISTS idx_eeg_poor_quality
ON sensor_eeg(session_id, time DESC)
WHERE quality_flag > 0;

-- ============================================================================
-- CONVENIENCE VIEWS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- VIEW: session_summary
-- Quick overview of all sessions with basic statistics
-- Use case: "Show me all sessions from last week"
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW session_summary AS
SELECT
    s.session_id,
    s.user_id,
    u.username,
    s.started_at,
    s.ended_at,
    s.ended_at - s.started_at AS session_duration,
    s.notes,
    -- Count calibration records for this session
    COUNT(DISTINCT sc.sensor_type) AS sensors_calibrated
FROM test_sessions s
LEFT JOIN users u ON s.user_id = u.user_id
LEFT JOIN sensor_calibration sc ON s.session_id = sc.session_id
GROUP BY s.session_id, s.user_id, u.username, s.started_at, s.ended_at, s.notes;

COMMENT ON VIEW session_summary IS 'Overview of all sessions with duration and sensor counts';

-- ----------------------------------------------------------------------------
-- VIEW: active_sessions
-- Currently running sessions (no end time)
-- Use case: "Is anyone currently testing?"
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW active_sessions AS
SELECT
    s.session_id,
    u.username,
    s.started_at,
    NOW() - s.started_at AS elapsed_time,
    s.notes
FROM test_sessions s
LEFT JOIN users u ON s.user_id = u.user_id
WHERE s.ended_at IS NULL
ORDER BY s.started_at DESC;

COMMENT ON VIEW active_sessions IS 'Currently running sessions without end times';

-- ----------------------------------------------------------------------------
-- VIEW: sensor_data_counts
-- Row counts for each sensor per session (useful for data quality checks)
-- Use case: "Did all sensors collect data? Why is eye tracking empty?"
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW sensor_data_counts AS
SELECT
    s.session_id,
    s.started_at,
    s.ended_at,
    (SELECT COUNT(*) FROM sensor_accelerometer WHERE session_id = s.session_id) AS accel_rows,
    (SELECT COUNT(*) FROM sensor_gyroscope WHERE session_id = s.session_id) AS gyro_rows,
    (SELECT COUNT(*) FROM sensor_eeg WHERE session_id = s.session_id) AS eeg_rows,
    (SELECT COUNT(*) FROM sensor_eye_tracking WHERE session_id = s.session_id) AS eye_rows,
    (SELECT COUNT(*) FROM sensor_heart_rate WHERE session_id = s.session_id) AS hr_rows,
    (SELECT COUNT(*) FROM sensor_oximeter WHERE session_id = s.session_id) AS oximeter_rows,
    (SELECT COUNT(*) FROM metrics_processed WHERE session_id = s.session_id) AS processed_rows
FROM test_sessions s
ORDER BY s.started_at DESC;

COMMENT ON VIEW sensor_data_counts IS 'Data volume per sensor per session - useful for identifying missing data';

-- ----------------------------------------------------------------------------
-- VIEW: sensor_health_summary
-- Overview of sensor status and calibration per session
-- Use case: "Why did the EEG data look weird? Check sampling rate and status"
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW sensor_health_summary AS
SELECT
    sc.session_id,
    sc.sensor_type,
    sc.sensor_status,
    sc.sampling_rate_hz,
    sc.calibration_timestamp,
    sc.hardware_version,
    sc.firmware_version,
    sc.notes
FROM sensor_calibration sc
ORDER BY sc.session_id, sc.sensor_type;

COMMENT ON VIEW sensor_health_summary IS 'Sensor configuration and health status for each session';

-- ----------------------------------------------------------------------------
-- VIEW: user_session_history
-- Complete history of sessions per user
-- Use case: "Show me all of patient_001's testing history for longitudinal analysis"
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW user_session_history AS
SELECT
    u.user_id,
    u.username,
    u.full_name,
    s.session_id,
    s.started_at,
    s.ended_at,
    s.ended_at - s.started_at AS duration,
    COUNT(DISTINCT sc.sensor_type) AS active_sensors
FROM users u
LEFT JOIN test_sessions s ON u.user_id = s.user_id
LEFT JOIN sensor_calibration sc ON s.session_id = sc.session_id
GROUP BY u.user_id, u.username, u.full_name, s.session_id, s.started_at, s.ended_at
ORDER BY u.username, s.started_at DESC;

COMMENT ON VIEW user_session_history IS 'Complete session history organized by user';

-- ============================================================================
-- TIMESCALEDB CONTINUOUS AGGREGATES
-- ============================================================================
-- COMMENTED OUT FOR WINDOWS TESTING (requires TimescaleDB extension)
-- Uncomment these sections when deploying to Raspberry Pi with TimescaleDB
-- ============================================================================

-- ----------------------------------------------------------------------------
-- CONTINUOUS AGGREGATE: eeg_100ms_avg
-- 100ms averages of EEG data (10 datapoints per second)
-- ----------------------------------------------------------------------------

-- CREATE MATERIALIZED VIEW IF NOT EXISTS eeg_100ms_avg
-- WITH (timescaledb.continuous) AS
-- SELECT
--     time_bucket('100 milliseconds', time) AS bucket,
--     session_id,
--     AVG(channel_1) AS avg_channel_1,
--     AVG(channel_2) AS avg_channel_2,
--     AVG(channel_3) AS avg_channel_3,
--     AVG(channel_4) AS avg_channel_4,
--     MIN(channel_1) AS min_channel_1,
--     MAX(channel_1) AS max_channel_1,
--     MIN(channel_2) AS min_channel_2,
--     MAX(channel_2) AS max_channel_2,
--     MIN(channel_3) AS min_channel_3,
--     MAX(channel_3) AS max_channel_3,
--     MIN(channel_4) AS min_channel_4,
--     MAX(channel_4) AS max_channel_4,
--     COUNT(*) AS sample_count
-- FROM sensor_eeg
-- GROUP BY bucket, session_id;

-- COMMENT ON MATERIALIZED VIEW eeg_100ms_avg IS '100ms averaged EEG data (10 datapoints/sec) for fast visualization';

-- Add refresh policy (auto-update the aggregate)
-- SELECT add_continuous_aggregate_policy('eeg_100ms_avg',
--     start_offset => INTERVAL '1 hour',
--     end_offset => INTERVAL '1 minute',
--     schedule_interval => INTERVAL '1 minute',
--     if_not_exists => TRUE);

-- ----------------------------------------------------------------------------
-- CONTINUOUS AGGREGATE: heart_rate_100ms_avg
-- 100ms averages of heart rate signal (10 datapoints/sec)
-- ----------------------------------------------------------------------------

-- CREATE MATERIALIZED VIEW IF NOT EXISTS heart_rate_100ms_avg
-- WITH (timescaledb.continuous) AS
-- SELECT
--     time_bucket('100 milliseconds', time) AS bucket,
--     session_id,
--     AVG(raw_signal) AS avg_signal,
--     MIN(raw_signal) AS min_signal,
--     MAX(raw_signal) AS max_signal,
--     COUNT(*) AS sample_count
-- FROM sensor_heart_rate
-- GROUP BY bucket, session_id;

-- COMMENT ON MATERIALIZED VIEW heart_rate_100ms_avg IS '100ms averaged heart rate signal (10 datapoints/sec)';

-- SELECT add_continuous_aggregate_policy('heart_rate_100ms_avg',
--     start_offset => INTERVAL '1 hour',
--     end_offset => INTERVAL '1 minute',
--     schedule_interval => INTERVAL '1 minute',
--     if_not_exists => TRUE);

-- ----------------------------------------------------------------------------
-- CONTINUOUS AGGREGATE: accelerometer_100ms_avg
-- 100ms averages of accelerometer data (10 datapoints/sec)
-- Includes magnitude calculation for tremor analysis
-- ----------------------------------------------------------------------------

-- CREATE MATERIALIZED VIEW IF NOT EXISTS accelerometer_100ms_avg
-- WITH (timescaledb.continuous) AS
-- SELECT
--     time_bucket('100 milliseconds', time) AS bucket,
--     session_id,
--     AVG(x) AS avg_x,
--     AVG(y) AS avg_y,
--     AVG(z) AS avg_z,
--     MIN(x) AS min_x,
--     MAX(x) AS max_x,
--     MIN(y) AS min_y,
--     MAX(y) AS max_y,
--     MIN(z) AS min_z,
--     MAX(z) AS max_z,
--     -- Calculate magnitude for tremor analysis
--     AVG(SQRT(x*x + y*y + z*z)) AS avg_magnitude,
--     COUNT(*) AS sample_count
-- FROM sensor_accelerometer
-- GROUP BY bucket, session_id;

-- COMMENT ON MATERIALIZED VIEW accelerometer_100ms_avg IS '100ms averaged accelerometer (10 datapoints/sec) with magnitude calculation';

-- SELECT add_continuous_aggregate_policy('accelerometer_100ms_avg',
--     start_offset => INTERVAL '1 hour',
--     end_offset => INTERVAL '1 minute',
--     schedule_interval => INTERVAL '1 minute',
--     if_not_exists => TRUE);

-- ----------------------------------------------------------------------------
-- CONTINUOUS AGGREGATE: gyroscope_100ms_avg
-- 100ms averages of gyroscope data (10 datapoints/sec)
-- ----------------------------------------------------------------------------

-- CREATE MATERIALIZED VIEW IF NOT EXISTS gyroscope_100ms_avg
-- WITH (timescaledb.continuous) AS
-- SELECT
--     time_bucket('100 milliseconds', time) AS bucket,
--     session_id,
--     AVG(x) AS avg_x,
--     AVG(y) AS avg_y,
--     AVG(z) AS avg_z,
--     MIN(x) AS min_x,
--     MAX(x) AS max_x,
--     MIN(y) AS min_y,
--     MAX(y) AS max_y,
--     MIN(z) AS min_z,
--     MAX(z) AS max_z,
--     COUNT(*) AS sample_count
-- FROM sensor_gyroscope
-- GROUP BY bucket, session_id;

-- COMMENT ON MATERIALIZED VIEW gyroscope_100ms_avg IS '100ms averaged gyroscope (10 datapoints/sec)';

-- SELECT add_continuous_aggregate_policy('gyroscope_100ms_avg',
--     start_offset => INTERVAL '1 hour',
--     end_offset => INTERVAL '1 minute',
--     schedule_interval => INTERVAL '1 minute',
--     if_not_exists => TRUE);

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- FUNCTION: get_session_time_range
-- Returns the earliest and latest timestamps for a given session
-- Useful for determining actual data collection period and data quality
-- Use case: "What time range did each sensor actually collect data?"
-- ----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION get_session_time_range(p_session_id UUID)
RETURNS TABLE(
    sensor_type TEXT,
    earliest_time TIMESTAMPTZ,
    latest_time TIMESTAMPTZ,
    duration INTERVAL,
    row_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'accelerometer'::TEXT, MIN(time), MAX(time), MAX(time) - MIN(time), COUNT(*)
    FROM sensor_accelerometer WHERE session_id = p_session_id
    UNION ALL
    SELECT 'gyroscope'::TEXT, MIN(time), MAX(time), MAX(time) - MIN(time), COUNT(*)
    FROM sensor_gyroscope WHERE session_id = p_session_id
    UNION ALL
    SELECT 'eeg'::TEXT, MIN(time), MAX(time), MAX(time) - MIN(time), COUNT(*)
    FROM sensor_eeg WHERE session_id = p_session_id
    UNION ALL
    SELECT 'eye_tracking'::TEXT, MIN(time), MAX(time), MAX(time) - MIN(time), COUNT(*)
    FROM sensor_eye_tracking WHERE session_id = p_session_id
    UNION ALL
    SELECT 'heart_rate'::TEXT, MIN(time), MAX(time), MAX(time) - MIN(time), COUNT(*)
    FROM sensor_heart_rate WHERE session_id = p_session_id
    UNION ALL
    SELECT 'oximeter'::TEXT, MIN(time), MAX(time), MAX(time) - MIN(time), COUNT(*)
    FROM sensor_oximeter WHERE session_id = p_session_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_session_time_range IS 'Get time range and row count for each sensor in a session';

-- Example usage:
-- SELECT * FROM get_session_time_range('your-session-uuid-here');
