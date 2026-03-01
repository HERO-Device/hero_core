"""
HERO System - Test Session Model
Tracks individual data collection sessions
"""

from sqlalchemy import Column, Text, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base


class TestSession(Base):
    """
    Test session table - tracks individual patients assessment sessions.

    Created at login, closed when the full test battery completes.
    Acts as the central anchor for all data collected during a visit —
    game results, sensor readings, calibration records, and events
    are all foreign-keyed to session_id.

    A session is always linked to exactly one participant, but the link
    changes state at anonymisation:

        Pre-anonymisation:  user_id is set,  anon_id is NULL.
        Post-anonymisation: user_id is NULL, anon_id is set.

    This is enforced at the DB level by the participant_link_exclusive
    CHECK constraint (added in 08_anonymisation.sql).

    Columns:
        session_id:    Primary key, auto-generated UUID.
        user_id:       FK → users.user_id. NULL after anonymisation.
        anon_id:       FK → anon_demographics.anon_id. NULL before anonymisation.
        anonymised_at: UTC timestamp when anonymise_sessions.py processed this row.
        started_at:    UTC timestamp when the session was created (set by DB).
        ended_at:      UTC timestamp when end_session() was called. NULL if active.
        notes:         Optional free-text (e.g. consultation ID).

    Relationships:
        user:              Many-to-one → User.
        anon_demographics: Many-to-one → AnonDemographics.
        calibrations:      One-to-many → SensorCalibration.
        game_results:      One-to-many → GameResult.
    """
    __tablename__ = 'test_sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Pre-anonymisation link — nullable so it can be cleared at anonymisation time
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=True)

    # Post-anonymisation link — populated by anonymise_sessions.py
    anon_id       = Column(String, ForeignKey('anon_demographics.anon_id'), nullable=True)
    anonymised_at = Column(DateTime(timezone=True), nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ended_at   = Column(DateTime(timezone=True))
    notes      = Column(Text)

    # Relationships
    user              = relationship("User", back_populates="sessions")
    anon_demographics = relationship("AnonDemographics", back_populates="sessions")
    calibrations      = relationship("SensorCalibration", back_populates="session", cascade="all, delete-orphan")
    game_results      = relationship("GameResult", back_populates="session", cascade="all, delete-orphan")

    @property
    def is_anonymised(self) -> bool:
        """True if this session has been anonymised and detached from a real user."""
        return self.anonymised_at is not None

    def __repr__(self):
        """String representation for logging and debugging."""
        participant = f"anon={self.anon_id}" if self.is_anonymised else f"user_id={self.user_id}"
        return f"<TestSession(session_id='{self.session_id}', {participant}, started={self.started_at})>"
    