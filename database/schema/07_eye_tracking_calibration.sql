-- ============================================================================
-- HERO System - Eye Tracking Calibration Table
-- ============================================================================
-- Stores polynomial regression coefficients from 9-point gaze calibration.
-- One row per session. Used by EyeTrackingProcessor to compute gaze coords.
-- ============================================================================

CREATE TABLE IF NOT EXISTS calibration_eye_tracking (
    calibration_id  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID        NOT NULL UNIQUE REFERENCES test_sessions(session_id) ON DELETE CASCADE,
    timestamp       TIMESTAMPTZ NOT NULL,

    -- Polynomial regression coefficients (15 terms, degree-2 on 4 iris features)
    coeff_x         JSONB       NOT NULL,   -- model_x.coef_ as list
    coeff_y         JSONB       NOT NULL,   -- model_y.coef_ as list
    intercept_x     DOUBLE PRECISION NOT NULL,
    intercept_y     DOUBLE PRECISION NOT NULL,
    poly_degree     INTEGER     NOT NULL DEFAULT 2,

    -- Raw calibration data (for reproducibility / refit)
    calib_features  JSONB,   -- 9 x [lx, ly, rx, ry]
    calib_targets   JSONB,   -- 9 x [tx, ty] pixels

    notes           TEXT
);

COMMENT ON TABLE calibration_eye_tracking IS
    'Eye tracking gaze calibration — polynomial regression coefficients per session';
