"""
HERO System - Core Package Setup
Makes hero-core installable as a Python package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="hero-core",
    version="1.0.0",
    author="HERO Team - University of Warwick",
    author_email="your-email@warwick.ac.uk",
    description="Core database infrastructure for the HERO biomedical monitoring system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/HERO",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "hero_core": [
            "database/schema/*.sql",
        ],
    },
)