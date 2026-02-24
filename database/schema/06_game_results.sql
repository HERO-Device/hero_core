-- ============================================================================
-- HERO System - Game Results Schema
-- ============================================================================
-- Stores cognitive test results for analysis
-- ============================================================================

CREATE TABLE IF NOT EXISTS game_results (
    result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    
    -- Game identification
    game_name TEXT NOT NULL,  -- 'Spiral', 'Trail', 'Shapes', 'Memory'
    game_number INTEGER,      -- 1-4, order in session (1=Spiral, 2=Trail, 3=Shapes, 4=Memory)
    
    -- Timing
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL,
    duration_seconds FLOAT,
    
    -- Performance metrics
    final_score INTEGER,
    max_score INTEGER,
    accuracy_percent FLOAT,
    
    -- Detailed metrics (game-specific)
    correct_answers INTEGER,
    incorrect_answers INTEGER,
    missed_answers INTEGER,
    average_reaction_time_ms FLOAT,
    
    -- Additional data (JSON for game-specific fields)
    -- Spiral:  {classification, prediction_value, trace_file, augmented_features, n_points}
    -- Trail:   {completion_time, path_efficiency, path_smoothness, errors, circle_path, ...}
    -- Shapes:  {total_questions, correct, incorrect, accuracy_percent, avg_reaction_time_s, trial_log}
    -- Memory:  {score, total_trials, accuracy_percent, incorrect_count, avg_cell_distance, trial_log}
    game_data JSONB,
    
    -- Quality
    completion_status TEXT,  -- 'completed', 'abandoned', 'error'
    
    CONSTRAINT valid_duration CHECK (duration_seconds > 0),
    CONSTRAINT valid_accuracy CHECK (accuracy_percent >= 0 AND accuracy_percent <= 100)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_game_results_session ON game_results(session_id);
CREATE INDEX IF NOT EXISTS idx_game_results_game ON game_results(game_name);

COMMENT ON TABLE game_results IS 'Cognitive test game results for analysis';
