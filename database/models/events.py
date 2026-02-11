"""
HERO System - Events Model
Event tracking for games, interactions, and system events
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base


class Event(Base):
    """Event table - tracks all system events"""
    __tablename__ = 'events'

    event_id = Column(UUID(as_uuid=True), primary_key=True)
    time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False,
                        primary_key=True)

    # Event classification
    event_type = Column(String, nullable=False)
    event_category = Column(String, nullable=False)

    # Event details
    event_data = Column(JSONB)

    # Game-specific fields
    game_name = Column(String)
    game_number = Column(Integer)

    # User interaction fields
    screen_x = Column(Float)
    screen_y = Column(Float)

    def __repr__(self):
        if self.game_name:
            return f"<Event(type='{self.event_type}', game='{self.game_name}', game_num={self.game_number}, time={self.time})>"
        return f"<Event(type='{self.event_type}', category='{self.event_category}', time={self.time})>"
