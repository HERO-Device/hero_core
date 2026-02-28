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
    """
    Records a patient's informed consent agreement prior to data collection.

    One row per consent version per user. Tracks both global consent and
    per-sensor granular consent, supporting future scenarios where a patient
    may consent to some sensors but not others.

    Columns:
        consent_id:                      Primary key, auto-generated UUID.
        user_id:                         Foreign key → users.user_id.
        consent_version:                 Version string of the consent form e.g. 'v1.0'.
        consent_date:                    UTC timestamp when consent was recorded (set by DB).
        data_collection_consent:         Global consent to collect data.
        seven_day_anonymization_consent: Consent to anonymise data after 7 days.
        two_year_deletion_consent:       Consent to delete data after 2 years.
        eeg_consent:                     Consent for EEG data collection.
        eye_tracking_consent:            Consent for eye tracking data collection.
        motion_sensor_consent:           Consent for accelerometer/gyroscope collection.
        biometric_consent:               Consent for heart rate/SpO2 collection.
        is_active:                       False if consent has been revoked.
        revoked_at:                      UTC timestamp of revocation, if applicable.
        revocation_reason:               Free-text reason for revocation.
        signature:                       Digital or written signature record.
        consent_method:                  How consent was obtained: 'digital_signature', 'verbal', 'written'.
    """
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
        """String representation for logging and debugging."""
        return f"<UserConsent(user_id='{self.user_id}', version='{self.consent_version}', active={self.is_active})>"


class DataLifecycleLog(Base):
    """
    Audit trail for data lifecycle events such as anonymisation and deletion.

    Written by automated retention jobs or admin actions. Provides a
    tamper-evident record of what happened to patient data and when.

    Columns:
        log_id:       Primary key, auto-generated UUID.
        timestamp:    UTC timestamp of the action (set by DB).
        action_type:  What happened: 'anonymized', 'deleted', 'exported', 'accessed'.
        target_type:  What was acted on: 'user', 'session', 'sensor_data'.
        target_id:    UUID of the specific record that was acted on.
        performed_by: Who triggered the action: 'system_automated', 'admin_user'.
        details:      JSONB dict of any additional context.
    """
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
        """String representation for logging and debugging."""
        return f"<LifecycleLog(action='{self.action_type}', target='{self.target_type}', time={self.timestamp})>"


class RetentionPolicy(Base):
    """
    Configures how long different categories of data are retained.

    One row per data_type, defining when anonymisation and deletion should
    be triggered by automated retention jobs.

    Columns:
        policy_id:                Primary key, auto-generated UUID.
        data_type:                Unique identifier for the data category.
        anonymization_after_days: Days after collection before anonymisation. None = never.
        deletion_after_days:      Days after collection before deletion.
        policy_active:            Whether this policy is currently enforced.
        created_at:               UTC timestamp of policy creation (set by DB).
        updated_at:               UTC timestamp of last update (set by DB).
        notes:                    Free-text description or justification.
    """
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
        """String representation for logging and debugging."""
        return f"<RetentionPolicy(type='{self.data_type}', anon={self.anonymization_after_days}d, delete={self.deletion_after_days}d)>"
