"""
Game Results Model
Stores cognitive test results for analysis
"""

from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base


class GameResult(Base):
    """Cognitive test game results"""
    __tablename__ = 'game_results'
    
    result_id = Column(UUID(as_uuid=True), primary_key=True, server_default='uuid_generate_v4()')
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
    
    __table_args__ = (
        CheckConstraint('duration_seconds > 0', name='valid_duration'),
        CheckConstraint('accuracy_percent >= 0 AND accuracy_percent <= 100', name='valid_accuracy'),
    )
    
    def __repr__(self):
        return f"<GameResult(game='{self.game_name}', score={self.final_score}/{self.max_score})>"
        
