-- ============================================================================
-- HERO System - Events Schema
-- ============================================================================
-- Description: Event tracking for games, user interactions, and system events
-- Version: 1.0.0
-- ============================================================================

-- Enable TimescaleDB extension (if not already enabled)
-- COMMENTED OUT FOR WINDOWS TESTING - UNCOMMENT FOR RPI5
-- CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- EVENTS TABLE
-- ============================================================================
-- Tracks all system events: game start/end, user interactions, system events
-- ============================================================================

CREATE TABLE IF NOT EXISTS events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,

    -- Event classification
    event_type TEXT NOT NULL,  -- Specific event (e.g., 'game_start', 'user_click')
    event_category TEXT NOT NULL,  -- Broad category: 'game', 'interaction', 'system'

    -- Event details
    event_data JSONB,  -- Flexible storage for event-specific data

    -- Game-specific fields (NULL for non-game events)
    game_name TEXT,  -- 'memory_game', 'reaction_time_game', etc.
    game_number INTEGER,  -- Game order in session (1, 2, 3, 4)

    -- User interaction fields (NULL for non-interaction events)
    screen_x DOUBLE PRECISION,  -- Click X coordinate
    screen_y DOUBLE PRECISION,  -- Click Y coordinate

    CONSTRAINT valid_event_category CHECK (
        event_category IN ('game', 'interaction', 'system', 'rest')
    ),
    CONSTRAINT valid_game_number CHECK (
        game_number IS NULL OR (game_number >= 1 AND game_number <= 4)
    )
);

-- Convert to hypertable (time-series optimized)
-- COMMENTED OUT FOR WINDOWS TESTING - UNCOMMENT FOR RPI5
-- SELECT create_hypertable('events', 'time', if_not_exists => TRUE);

-- Indexes for common queries
CREATE INDEX idx_events_session ON events(session_id, time DESC);
CREATE INDEX idx_events_type ON events(event_type, time DESC);
CREATE INDEX idx_events_category ON events(event_category, time DESC);
CREATE INDEX idx_events_game ON events(game_name, time DESC) WHERE game_name IS NOT NULL;

COMMENT ON TABLE events IS 'All system events: games, user interactions, system events';
COMMENT ON COLUMN events.event_type IS 'Specific event: game_start, game_end, user_click, correct_answer, incorrect_answer, rest_start, rest_end, sensor_failure';
COMMENT ON COLUMN events.event_category IS 'Broad category: game, interaction, system, rest';
COMMENT ON COLUMN events.game_number IS 'Game order in session (1-4), NULL for non-game events';
COMMENT ON COLUMN events.event_data IS 'Flexible JSON storage for event-specific data (scores, reaction times, error messages)';

-- ============================================================================
-- STANDARD EVENT TYPES
-- ============================================================================
-- Documentation of standard event types used in the system

COMMENT ON COLUMN events.event_type IS
'Standard event types:
GAME EVENTS:
- game_start: Game begins
- game_end: Game completes
- level_start: New level within game
- level_complete: Level finished
- correct_answer: User answered correctly
- incorrect_answer: User answered incorrectly
- game_paused: User paused game
- game_resumed: User resumed game

REST EVENTS:
- rest_start: Rest period begins
- rest_end: Rest period ends

INTERACTION EVENTS:
- button_click: User clicked button
- screen_tap: User tapped screen
- key_press: Keyboard input

SYSTEM EVENTS:
- session_start: Session begins
- session_end: Session completes
- sensor_started: Sensor began recording
- sensor_stopped: Sensor stopped
- sensor_failure: Sensor error
- sensor_recovered: Sensor resumed after failure
- calibration_start: Calibration begins
- calibration_complete: Calibration finished';

-- ============================================================================
-- EXAMPLE EVENT DATA STRUCTURES
-- ============================================================================
-- Examples of how event_data JSONB should be structured

COMMENT ON COLUMN events.event_data IS
'Example event_data structures:

GAME_START:
{
  "game_id": "memory_game",
  "difficulty": "medium",
  "game_number": 1
}

GAME_END:
{
  "game_id": "memory_game",
  "final_score": 8,
  "max_score": 10,
  "duration_seconds": 120,
  "game_number": 1
}

CORRECT_ANSWER:
{
  "game_id": "memory_game",
  "question_number": 3,
  "reaction_time_ms": 850,
  "stimulus": "pattern_sequence_abc"
}

INCORRECT_ANSWER:
{
  "game_id": "reaction_time_game",
  "question_number": 5,
  "reaction_time_ms": 1200,
  "user_answer": "left",
  "correct_answer": "right"
}

USER_CLICK:
{
  "button_id": "submit_answer",
  "button_label": "Next"
}

SENSOR_FAILURE:
{
  "sensor_type": "eeg",
  "error_message": "Connection lost",
  "error_code": "CONN_TIMEOUT"
}

REST_START:
{
  "rest_number": 1,
  "duration_seconds": 30
}';