"""
Database connection management using SQLAlchemy + SQLite.
Uses the existing brainfeed.db file from the JS version.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Path to existing SQLite DB (one level up from backend/)
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "db")
DB_PATH = os.path.join(DB_DIR, "brainfeed.db")

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Handle "postgres://" deprecation in SQLAlchemy 1.4+
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(DATABASE_URL, echo=False)
else:
    # Fallback to SQLite (Local Development)
    SQLALCHEMY_DATABASE_URL = "sqlite:///./brainfeed.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    from backend.db.models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)
    print(f"[DB] Initialized SQLite database at {DB_PATH}")
