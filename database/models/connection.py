"""
HERO System - Database Connection Helpers
Utilities for creating database connections
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_db_engine(host='localhost', port=5432, user='postgres', password='', dbname='hero_db', echo=False):
    """
    Create SQLAlchemy engine for database connection

    Args:
        host: Database host
        port: Database port
        user: Database user
        password: Database password
        dbname: Database name
        echo: If True, log all SQL statements (useful for debugging)

    Returns:
        SQLAlchemy engine
    """
    connection_string = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
    engine = create_engine(connection_string, echo=echo)
    return engine


def create_db_session(engine):
    """
    Create SQLAlchemy session from engine

    Args:
        engine: SQLAlchemy engine

    Returns:
        SQLAlchemy session
    """
    Session = sessionmaker(bind=engine)
    return Session()


def get_db_connection(host='localhost', port=5432, user='postgres', password='', dbname='hero_db', echo=False):
    """
    Convenience function to get both engine and session

    Args:
        host: Database host
        port: Database port
        user: Database user
        password: Database password
        dbname: Database name
        echo: If True, log all SQL statements

    Returns:
        tuple: (engine, session)
    """
    engine = create_db_engine(host, port, user, password, dbname, echo)
    session = create_db_session(engine)
    return engine, session
