-- ============================================================================
-- HERO System - Core Tables Schema
-- ============================================================================
-- Description: Core user and session management tables
-- Version: 1.0.0
-- ============================================================================

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Stores user information
-- NOTE: Ethics/anonymization will be added later by the team
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    -- Primary identifier
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- User information
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    full_name TEXT,
    date_of_birth DATE,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT username_not_empty CHECK (char_length(username) > 0),
    CONSTRAINT valid_email CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Index for lookup by username
CREATE INDEX idx_users_username ON users(username);

-- ============================================================================
-- TEST SESSIONS TABLE
-- ============================================================================
-- Tracks individual cognitive testing sessions
-- Each session = user plays games while sensors collect biometric data
-- ============================================================================

CREATE TABLE IF NOT EXISTS test_sessions (
    -- Primary identifier
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Relationships
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Timing
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,

    -- Optional metadata
    notes TEXT,

    -- Constraints
    CONSTRAINT valid_session_duration CHECK (ended_at IS NULL OR ended_at >= started_at)
);

-- Indexes for common queries
CREATE INDEX idx_sessions_user ON test_sessions(user_id);
CREATE INDEX idx_sessions_started ON test_sessions(started_at DESC);

-- Index for finding active sessions
CREATE INDEX idx_sessions_active ON test_sessions(started_at) WHERE ended_at IS NULL;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users IS 'Stores user information for HERO system participants';
COMMENT ON TABLE test_sessions IS 'Cognitive testing sessions where users play games while biometric data is collected';
COMMENT ON COLUMN test_sessions.notes IS 'Optional session notes (e.g., equipment issues, participant behavior)';