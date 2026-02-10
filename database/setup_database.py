#!/usr/bin/env python3
"""
HERO System - Database Setup Script
Automated PostgreSQL + TimescaleDB setup
"""

import sys
import argparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path


def create_database(host, port, user, password, db_name):
    """Create the PostgreSQL database if it doesn't exist"""
    try:
        # Connect to default 'postgres' database to create our database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()

        if not exists:
            print(f"Creating database '{db_name}'...")
            cursor.execute(f'CREATE DATABASE {db_name}')
            print(f"✓ Database '{db_name}' created successfully")
        else:
            print(f"✓ Database '{db_name}' already exists")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False


def run_sql_file(conn, file_path):
    """Execute SQL commands from a file"""
    try:
        with open(file_path, 'r') as f:
            sql = f.read()

        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()

        print(f"✓ Executed: {file_path.name}")
        return True

    except Exception as e:
        print(f"✗ Error executing {file_path.name}: {e}")
        conn.rollback()
        return False


def setup_database(host, port, user, password, db_name, schema_dir):
    """Run all schema files in order"""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name
        )

        print(f"\n{'=' * 60}")
        print(f"Setting up HERO database schema...")
        print(f"{'=' * 60}\n")

        # Get all SQL files in order
        schema_files = sorted(schema_dir.glob('*.sql'))

        if not schema_files:
            print(f"✗ No SQL files found in {schema_dir}")
            return False

        # Execute each file
        success = True
        for sql_file in schema_files:
            if not run_sql_file(conn, sql_file):
                success = False
                break

        conn.close()

        if success:
            print(f"\n{'=' * 60}")
            print(f"✓ Database setup completed successfully!")
            print(f"{'=' * 60}\n")
        else:
            print(f"\n{'=' * 60}")
            print(f"✗ Database setup failed")
            print(f"{'=' * 60}\n")

        return success

    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Setup HERO PostgreSQL + TimescaleDB database'
    )
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', default='5432', help='Database port')
    parser.add_argument('--user', default='postgres', help='Database user')
    parser.add_argument('--password', help='Database password (will prompt if not provided)')
    parser.add_argument('--dbname', default='hero_db', help='Database name')
    parser.add_argument('--schema-dir', help='Path to schema directory (auto-detected if not provided)')

    args = parser.parse_args()

    # Get password if not provided
    password = args.password
    if not password:
        import getpass
        password = getpass.getpass(f"Enter password for user '{args.user}': ")

    # Find schema directory
    if args.schema_dir:
        schema_dir = Path(args.schema_dir)
    else:
        # Auto-detect: assume we're in database/ directory
        script_dir = Path(__file__).parent
        schema_dir = script_dir / 'schema'

    if not schema_dir.exists():
        print(f"✗ Schema directory not found: {schema_dir}")
        sys.exit(1)

    print(f"\nHERO Database Setup")
    print(f"{'=' * 60}")
    print(f"Host:     {args.host}:{args.port}")
    print(f"Database: {args.dbname}")
    print(f"User:     {args.user}")
    print(f"Schema:   {schema_dir}")
    print(f"{'=' * 60}\n")

    # Create database
    if not create_database(args.host, args.port, args.user, password, args.dbname):
        sys.exit(1)

    # Setup schema
    if not setup_database(args.host, args.port, args.user, password, args.dbname, schema_dir):
        sys.exit(1)

    print("\n✓ HERO database is ready to use!\n")


if __name__ == '__main__':
    main()
