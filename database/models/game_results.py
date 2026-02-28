"""
Game Results Model
Stores cognitive test results for analysis
"""

from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base
import uuid


class GameResult(Base):
    """Cognitive test game results"""
    """
    Stores the outcome of the games within a session.

    One row is written per game per session by Consultation._save_game_to_db()
    after each test completes. The raw results dict from each game module
    is stored in game_data for flexibility.

    Columns:
        result_id:               Primary key, auto-generated UUID.
        session_id:              Foreign key → test_sessions.session_id.
        game_name:               Game identifier: 'Spiral', 'Trail', 'Shapes', 'Memory'.
        game_number:             Ordinal position of the game in the session (0-indexed).
        started_at:              UTC timestamp when the game loop began.
        completed_at:            UTC timestamp when the game loop ended.
        duration_seconds:        Derived from completed_at - started_at.
        final_score:             Raw score achieved (None for untimed/unscored games like Spiral).
        max_score:               Maximum possible score for this game.
        accuracy_percent:        Score as a percentage of max_score.
        correct_answers:         Count of correct responses.
        incorrect_answers:       Count of incorrect responses.
        missed_answers:          Count of unanswered prompts.
        average_reaction_time_ms: Mean response time across all trials in ms.
        game_data:               JSONB dict of full game-specific results from module.results.
        completion_status:       Typically 'completed'. Reserved for 'abandoned', 'error', etc.

    Relationships:
        session: Many-to-one → TestSession.
    """
    __tablename__ = 'game_results'
    
    result_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default='uuid_generate_v4()')
    session_id = Column(UUID(as_uuid=True), ForeignKey('test_sessions.session_id', ondelete='CASCADE'), nullable=False)
    
    # Game identification
    game_name = Column(String, nullable=False)
    game_number = Column(Integer)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=False)
    duration_seconds = Column(Float)
    
    # Performance metrics
    final_score = Column(Integer)
    max_score = Column(Integer)
    accuracy_percent = Column(Float)
    
    # Detailed metrics
    correct_answers = Column(Integer)
    incorrect_answers = Column(Integer)
    missed_answers = Column(Integer)
    average_reaction_time_ms = Column(Float)
    
    # Additional data
    game_data = Column(JSONB)
    
    # Quality
    completion_status = Column(String)

    # Relationships
    session = relationship("TestSession", back_populates="game_results")
    
    __table_args__ = (
        CheckConstraint('duration_seconds > 0', name='valid_duration'),
        CheckConstraint('accuracy_percent >= 0 AND accuracy_percent <= 100', name='valid_accuracy'),
    )
    
    def __repr__(self):
        """String representation for logging and debugging."""
        return f"<GameResult(game='{self.game_name}', score={self.final_score}/{self.max_score})>"
