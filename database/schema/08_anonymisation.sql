-- ============================================================================
-- HERO System - Anonymisation Schema
-- ============================================================================
-- Description: Adds anonymous demographics table and migrates test_sessions
--              to support a two-state participant link:
--                - Pre-anonymisation:  test_sessions.user_id  is set, anon_id is NULL
--                - Post-anonymisation: test_sessions.user_id  is NULL, anon_id is set
--
-- Age ranges supported (neurodegenerative disease research population):
--   18-24, 25-30, 31-40, 41-50, 51-60, 61-70
--
-- Version: 1.0.0
-- Run after: 07_eye_tracking_calibration.sql
-- ============================================================================


-- ============================================================================
-- ANONYMOUS DEMOGRAPHICS TABLE
-- ============================================================================
-- Each row represents a cohort label (e.g. "testing_stage_1") with an
-- associated age range. Multiple sessions can share the same anon_id,
-- which is intentional — sessions in the same testing cohort and age band
-- are grouped together, preventing re-identification through session counts.
-- ============================================================================

CREATE TABLE IF NOT EXISTS anon_demographics (
    anon_id     TEXT PRIMARY KEY,   -- Human-readable cohort label e.g. "testing_stage_1"
    age_range   TEXT NOT NULL,      -- One of the defined age bands below

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_age_range CHECK (
        age_range IN ('18-24', '25-30', '31-40', '41-50', '51-60', '61-70')
    )
);

COMMENT ON TABLE anon_demographics IS
    'Anonymous demographic stubs that sessions are re-linked to after anonymisation. '
    'Each row is a cohort label + age band — sessions in the same cohort share a row.';

COMMENT ON COLUMN anon_demographics.anon_id IS
    'Human-readable cohort identifier assigned at anonymisation time e.g. "testing_stage_1". '
    'Generated automatically by the anonymise_sessions.py script.';

COMMENT ON COLUMN anon_demographics.age_range IS
    'Broad age band calculated from date_of_birth at session started_at. '
    'Replaces exact DOB so the session retains demographic utility without PII.';


-- ============================================================================
-- MIGRATE test_sessions
-- ============================================================================
-- 1. Allow user_id to be NULL (sessions become ownerless after anonymisation).
-- 2. Add anon_id FK → anon_demographics.
-- 3. Add anonymised_at timestamp so we can filter out already-processed sessions.
-- ============================================================================

-- Drop the NOT NULL constraint on user_id
ALTER TABLE test_sessions
    ALTER COLUMN user_id DROP NOT NULL;

-- Add anon_id column (nullable FK — only populated post-anonymisation)
ALTER TABLE test_sessions
    ADD COLUMN IF NOT EXISTS anon_id TEXT REFERENCES anon_demographics(anon_id),
    ADD COLUMN IF NOT EXISTS anonymised_at TIMESTAMPTZ;

-- Enforce: a session must always have exactly one of user_id or anon_id set.
-- This prevents orphaned sessions (both NULL) or double-linked sessions (both set).
ALTER TABLE test_sessions
    ADD CONSTRAINT participant_link_exclusive CHECK (
        (user_id IS NOT NULL AND anon_id IS NULL)
        OR
        (user_id IS NULL AND anon_id IS NOT NULL)
    );

-- Index for lookups by cohort label
CREATE INDEX IF NOT EXISTS idx_sessions_anon ON test_sessions(anon_id);

COMMENT ON COLUMN test_sessions.user_id IS
    'FK → users. Populated pre-anonymisation. Set to NULL when anonymised.';

COMMENT ON COLUMN test_sessions.anon_id IS
    'FK → anon_demographics. NULL pre-anonymisation. Populated when anonymised.';

COMMENT ON COLUMN test_sessions.anonymised_at IS
    'UTC timestamp when anonymise_sessions.py processed this session. NULL = not yet anonymised.';


-- ============================================================================
-- PATCH users TABLE
-- ============================================================================
-- The anonymize_old_users() function defined in 04_ethics_tables.sql
-- references is_anonymized and anonymized_at columns that were never created.
-- Add them here so the existing function doesn't error on execution.
-- ============================================================================

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS is_anonymized   BOOLEAN     NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS anonymized_at   TIMESTAMPTZ;

COMMENT ON COLUMN users.is_anonymized IS
    'TRUE once the user''s PII has been scrubbed by anonymise_sessions.py.';

COMMENT ON COLUMN users.anonymized_at IS
    'UTC timestamp when PII was scrubbed from this user row.';