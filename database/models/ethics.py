"""
HERO System - Ethics & Consent Models
User consent, data lifecycle audit, and retention policies
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base


class UserConsent(Base):
    """User consent agreements for data collection and retention"""
    __tablename__ = 'user_consent'

    consent_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)

    # Consent details
    consent_version = Column(String, nullable=False)  # e.g., "v1.0"
    consent_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Specific consents
    data_collection_consent = Column(Boolean, nullable=False)
    seven_day_anonymization_consent = Column(Boolean, nullable=False)
    two_year_deletion_consent = Column(Boolean, nullable=False)

    # Sensor-specific consents
    eeg_consent = Column(Boolean, default=True)
    eye_tracking_consent = Column(Boolean, default=True)
    motion_sensor_consent = Column(Boolean, default=True)
    biometric_consent = Column(Boolean, default=True)

    # Consent status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True))
    revocation_reason = Column(Text)

    # Signature
    signature = Column(Text)
    consent_method = Column(String)  # 'digital_signature', 'verbal', 'written'

    def __repr__(self):
        return f"<UserConsent(user_id='{self.user_id}', version='{self.consent_version}', active={self.is_active})>"


class DataLifecycleLog(Base):
    """Audit trail for data lifecycle events"""
    __tablename__ = 'data_lifecycle_log'

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Action details
    action_type = Column(String, nullable=False)  # 'anonymized', 'deleted', 'exported', 'accessed'
    target_type = Column(String, nullable=False)  # 'user', 'session', 'sensor_data'
    target_id = Column(UUID(as_uuid=True))

    # Who performed the action
    performed_by = Column(String, nullable=False)  # 'system_automated', 'admin_user'

    # Additional details
    details = Column(JSONB)

    def __repr__(self):
        return f"<LifecycleLog(action='{self.action_type}', target='{self.target_type}', time={self.timestamp})>"


class RetentionPolicy(Base):
    """Configurable retention periods for different data types"""
    __tablename__ = 'retention_policies'

    policy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_type = Column(String, unique=True, nullable=False)

    # Retention periods (in days)
    anonymization_after_days = Column(Integer)  # NULL = no anonymization
    deletion_after_days = Column(Integer, nullable=False)

    # Policy status
    policy_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    notes = Column(Text)

    def __repr__(self):
        return f"<RetentionPolicy(type='{self.data_type}', anon={self.anonymization_after_days}d, delete={self.deletion_after_days}d)>"
