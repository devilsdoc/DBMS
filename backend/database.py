"""
Database connection and session factory for FastAPI backend.
Supports both PostgreSQL (via DATABASE_URL) and SQLite (cse_attendance.db fallback).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres@localhost:5432/cse_attendance"
)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SQLITE_PATH = os.path.join(BASE_DIR, "cse_attendance.db")
SQLITE_URL = f"sqlite:///{SQLITE_PATH.replace(os.sep, '/')}"

# Fallback engine detector
def create_app_engine():
    if os.getenv("USE_SQLITE", "false").lower() == "true":
        return create_engine(SQLITE_URL, echo=False, connect_args={"check_same_thread": False})
    
    try:
        eng = create_engine(POSTGRES_URL, echo=False, connect_args={"connect_timeout": 2})
        with eng.connect() as conn:
            pass
        return eng
    except Exception:
        # Fall back to SQLite if Postgres is unreachable
        return create_engine(SQLITE_URL, echo=False, connect_args={"check_same_thread": False})

engine = create_app_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
