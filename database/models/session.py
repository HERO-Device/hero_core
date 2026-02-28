"""
HERO System - Test Session Model
Tracks individual data collection sessions
"""

from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base


class TestSession(Base):
    """Test session table - tracks individual data collection sessions"""
    """
    Test session table - tracks individual patients assessment sessions

    Created at login, closed when the full test battery completes.
    Acts as the central anchor for all data collected during a visit —
    game results, sensor readings, calibration records, and events
    are all foreign-keyed to session_id.

    Columns:
        session_id: Primary key, auto-generated UUID.
        user_id:    Foreign key → users.user_id.
        started_at: UTC timestamp when the session was created (set by DB).
        ended_at:   UTC timestamp when end_session() was called. NULL if active.
        notes:      Optional free-text (e.g. consultation ID).

    Relationships:
        user:         Many-to-one → User.
        calibrations: One-to-many → SensorCalibration.
        game_results: One-to-many → GameResult.
    """
    __tablename__ = 'test_sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    notes = Column(Text)

    # Relationships
    user = relationship("User", back_populates="sessions")
    calibrations = relationship("SensorCalibration", back_populates="session", cascade="all, delete-orphan")
    game_results = relationship("GameResult", back_populates="session", cascade="all, delete-orphan")  # ADD THIS LINE

    def __repr__(self):
        """String representation for logging and debugging."""
        return f"<TestSession(session_id='{self.session_id}', user_id='{self.user_id}', started={self.started_at})>"
