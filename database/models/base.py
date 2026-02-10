"""
HERO System - Database Base
SQLAlchemy declarative base and shared imports
"""

from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base that all models will inherit from
Base = declarative_base()
