from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------------------------
# Database Configuration
# -------------------------

# SQLite (Development)
DATABASE_URL = "sqlite:///./accidents.db"

# Example for Production (PostgreSQL)
# DATABASE_URL = "postgresql://user:password@localhost/accident_db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()
