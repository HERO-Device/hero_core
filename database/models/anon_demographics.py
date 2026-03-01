"""
HERO System - Anonymous Demographics Model
Cohort stubs that sessions are re-linked to after anonymisation.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


# Age ranges supported for the HERO research population.
# Covers the neurodegenerative disease study demographic (18–70).
AGE_RANGES = ("18-24", "25-30", "31-40", "41-50", "51-60", "61-70")


class AnonDemographics(Base):
    """
    Anonymous demographic stubs used to re-link sessions after anonymisation.

    Each row represents a cohort label paired with an age band.
    Multiple sessions can share the same anon_id — this is intentional,
    as grouping sessions by cohort + age band prevents re-identification
    through session counts alone.

    The anon_id label (e.g. "testing_stage_1") is generated automatically
    by anonymise_sessions.py at the time of anonymisation.

    Columns:
        anon_id:    Primary key. Human-readable cohort label.
        age_range:  Broad age band e.g. "41-50". Calculated from the
                    patient's date_of_birth relative to session.started_at.
        created_at: UTC timestamp when this demographics record was created.

    Relationships:
        sessions: One-to-many → TestSession (via anon_id FK).
    """
    __tablename__ = "anon_demographics"

    anon_id    = Column(String, primary_key=True)
    age_range  = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationship back to sessions that have been anonymised into this cohort
    sessions = relationship("TestSession", back_populates="anon_demographics")

    def __repr__(self):
        return f"<AnonDemographics(anon_id='{self.anon_id}', age_range='{self.age_range}')>"