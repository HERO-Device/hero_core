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
        return f"<TestSession(session_id='{self.session_id}', user_id='{self.user_id}', started={self.started_at})>"
        
