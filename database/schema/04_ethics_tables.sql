-- ============================================================================
-- HERO System - Ethics & Compliance Schema
-- ============================================================================
-- Description: Consent tracking, data lifecycle audit, and retention policies
-- Version: 1.0.0
-- ============================================================================

-- ============================================================================
-- USER CONSENT TABLE
-- ============================================================================
-- Tracks user consent agreements for data collection and retention
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_consent (
    consent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Consent details
    consent_version TEXT NOT NULL,  -- Version of consent form (e.g., "v1.0")
    consent_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Specific consents
    data_collection_consent BOOLEAN NOT NULL,  -- General data collection
    seven_day_anonymization_consent BOOLEAN NOT NULL,  -- Agrees to 7-day anonymization
    two_year_deletion_consent BOOLEAN NOT NULL,  -- Agrees to 2-year deletion

    -- Sensor-specific consents
    eeg_consent BOOLEAN DEFAULT TRUE,
    eye_tracking_consent BOOLEAN DEFAULT TRUE,
    motion_sensor_consent BOOLEAN DEFAULT TRUE,
    biometric_consent BOOLEAN DEFAULT TRUE,  -- Heart rate, SpO2

    -- Consent status
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMPTZ,
    revocation_reason TEXT,

    -- Signature/acknowledgment
    signature TEXT,  -- Could be typed name or digital signature
    consent_method TEXT,  -- 'digital_signature', 'verbal', 'written'

    CONSTRAINT valid_revocation CHECK (
        (is_active = TRUE AND revoked_at IS NULL) OR
        (is_active = FALSE AND revoked_at IS NOT NULL)
    )
);

CREATE INDEX idx_consent_user ON user_consent(user_id);
CREATE INDEX idx_consent_active ON user_consent(user_id, is_active) WHERE is_active = TRUE;

COMMENT ON TABLE user_consent IS 'User consent agreements for data collection and retention policies';
COMMENT ON COLUMN user_consent.seven_day_anonymization_consent IS 'User agrees that personal data will be anonymized after 7 days';
COMMENT ON COLUMN user_consent.two_year_deletion_consent IS 'User agrees that all data will be deleted after 2 years';

-- ============================================================================
-- DATA LIFECYCLE LOG TABLE
-- ============================================================================
-- Audit trail for data anonymization, deletion, and access
-- ============================================================================

CREATE TABLE IF NOT EXISTS data_lifecycle_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Action details
    action_type TEXT NOT NULL,  -- 'anonymized', 'deleted', 'exported', 'accessed'
    target_type TEXT NOT NULL,  -- 'user', 'session', 'sensor_data'
    target_id UUID,  -- ID of affected record

    -- Who performed the action
    performed_by TEXT NOT NULL,  -- 'system_automated', 'admin_user', 'export_request'

    -- Additional details
    details JSONB,  -- Flexible storage for action-specific data

    CONSTRAINT valid_action_type CHECK (
        action_type IN ('anonymized', 'deleted', 'exported', 'accessed', 'consent_revoked')
    ),
    CONSTRAINT valid_target_type CHECK (
        target_type IN ('user', 'session', 'sensor_data', 'all_user_data')
    )
);

CREATE INDEX idx_lifecycle_timestamp ON data_lifecycle_log(timestamp DESC);
CREATE INDEX idx_lifecycle_action ON data_lifecycle_log(action_type, timestamp DESC);
CREATE INDEX idx_lifecycle_target ON data_lifecycle_log(target_id);

COMMENT ON TABLE data_lifecycle_log IS 'Audit trail for data lifecycle events (anonymization, deletion, export)';

-- ============================================================================
-- RETENTION POLICIES TABLE
-- ============================================================================
-- Configurable retention periods for different data types
-- ============================================================================

CREATE TABLE IF NOT EXISTS retention_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_type TEXT UNIQUE NOT NULL,

    -- Retention periods (in days)
    anonymization_after_days INTEGER,  -- NULL = no anonymization
    deletion_after_days INTEGER NOT NULL,

    -- Policy status
    policy_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes TEXT,

    CONSTRAINT positive_days CHECK (
        anonymization_after_days IS NULL OR anonymization_after_days > 0
    ),
    CONSTRAINT deletion_after_anonymization CHECK (
        anonymization_after_days IS NULL OR
        deletion_after_days > anonymization_after_days
    )
);

-- Insert default retention policies
INSERT INTO retention_policies (data_type, anonymization_after_days, deletion_after_days, notes)
VALUES
    ('user_info', 7, 730, 'Personal user information - anonymize after 7 days, delete after 2 years'),
    ('raw_sensor_data', NULL, 730, 'Raw sensor data - no anonymization, delete after 2 years'),
    ('processed_metrics', NULL, 730, 'Processed metrics - no anonymization, delete after 2 years'),
    ('session_metadata', NULL, 730, 'Session metadata - no anonymization, delete after 2 years'),
    ('events', NULL, 730, 'Event logs - no anonymization, delete after 2 years'),
    ('consent_records', NULL, 3650, 'Consent records - keep for 10 years for legal compliance')
ON CONFLICT (data_type) DO NOTHING;

CREATE INDEX idx_retention_active ON retention_policies(data_type) WHERE policy_active = TRUE;

COMMENT ON TABLE retention_policies IS 'Configurable retention policies for different data types';

-- ============================================================================
-- ANONYMIZATION FUNCTION
-- ============================================================================
-- Automatically anonymize user data after 7 days
-- ============================================================================

CREATE OR REPLACE FUNCTION anonymize_old_users()
RETURNS INTEGER AS $$
DECLARE
    user_record RECORD;
    anonymized_count INTEGER := 0;
    retention_days INTEGER;
BEGIN
    -- Get retention period for user_info
    SELECT anonymization_after_days INTO retention_days
    FROM retention_policies
    WHERE data_type = 'user_info' AND policy_active = TRUE;

    IF retention_days IS NULL THEN
        RETURN 0;  -- Anonymization disabled
    END IF;

    -- Anonymize users older than retention period
    FOR user_record IN
        SELECT user_id, username, created_at
        FROM users
        WHERE created_at < NOW() - (retention_days || ' days')::INTERVAL
        AND NOT is_anonymized
    LOOP
        -- Anonymize the user
        UPDATE users
        SET
            email = 'anonymized@hero.local',
            full_name = 'ANONYMIZED',
            date_of_birth = NULL,
            username = 'anon_' || LEFT(user_id::TEXT, 8),
            is_anonymized = TRUE,
            anonymized_at = NOW()
        WHERE user_id = user_record.user_id;

        -- Log the anonymization
        INSERT INTO data_lifecycle_log
            (timestamp, action_type, target_type, target_id, performed_by, details)
        VALUES
            (NOW(), 'anonymized', 'user', user_record.user_id, 'system_automated',
             jsonb_build_object(
                 'original_username', user_record.username,
                 'days_since_creation', EXTRACT(DAY FROM NOW() - user_record.created_at),
                 'retention_policy_days', retention_days
             ));

        anonymized_count := anonymized_count + 1;
    END LOOP;

    RETURN anonymized_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION anonymize_old_users IS 'Anonymize user data older than retention policy (7 days)';

-- ============================================================================
-- DATA DELETION FUNCTION
-- ============================================================================
-- Delete all user data after 2 years
-- ============================================================================

CREATE OR REPLACE FUNCTION delete_old_data()
RETURNS INTEGER AS $$
DECLARE
    session_record RECORD;
    deleted_count INTEGER := 0;
    retention_days INTEGER;
BEGIN
    -- Get retention period for raw sensor data
    SELECT deletion_after_days INTO retention_days
    FROM retention_policies
    WHERE data_type = 'raw_sensor_data' AND policy_active = TRUE;

    IF retention_days IS NULL THEN
        RETURN 0;  -- Deletion disabled
    END IF;

    -- Delete sessions (and cascade to sensor data) older than 2 years
    FOR session_record IN
        SELECT session_id, started_at
        FROM test_sessions
        WHERE started_at < NOW() - (retention_days || ' days')::INTERVAL
    LOOP
        -- Log before deletion
        INSERT INTO data_lifecycle_log
            (timestamp, action_type, target_type, target_id, performed_by, details)
        VALUES
            (NOW(), 'deleted', 'session', session_record.session_id, 'system_automated',
             jsonb_build_object(
                 'session_date', session_record.started_at,
                 'days_since_session', EXTRACT(DAY FROM NOW() - session_record.started_at),
                 'retention_policy_days', retention_days
             ));

        -- Delete session (cascades to all sensor data)
        DELETE FROM test_sessions WHERE session_id = session_record.session_id;

        deleted_count := deleted_count + 1;
    END LOOP;

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION delete_old_data IS 'Delete all data (sessions and sensor data) older than 2 years';