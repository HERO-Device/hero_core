"""
HERO System - User Model
Stores participant information
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base


class User(Base):
    """
    User table - stores HERO participant information

    Each User maps to a single patient account. All test sessions,
    sensor readings, and game results are linked back to a user
    via test_sessions.

    Columns:
        user_id:       Primary key, auto-generated UUID.
        username:      Unique login handle.
        password:      Plaintext — to be hashed in a future security pass.
        email:         Optional contact email.
        full_name:     Patient display name.
        date_of_birth: Optional, for demographic analysis.
        created_at:    UTC timestamp of account creation (set by DB).
        updated_at:    UTC timestamp of last update (set by DB).

    Relationships:
        sessions: One-to-many → TestSession.
    """
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String)
    full_name = Column(String)
    date_of_birth = Column(DateTime)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("TestSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation for logging and debugging."""
        return f"<User(username='{self.username}', user_id='{self.user_id}')>"
