"""
Database configuration and connection management
PostgreSQL setup for Crypto Analytics Platform
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/crypto_analytics")

# For development, you can also use SQLite as fallback
SQLITE_FALLBACK = "sqlite:///./crypto_analytics.db"

# Create engine with connection pooling
try:
    # Try PostgreSQL first
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False  # Set to True for SQL debugging
    )
    
    # Test the connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    
    logger.info("✅ Connected to PostgreSQL database")
    DB_TYPE = "postgresql"
    
except Exception as e:
    logger.warning(f"⚠️ PostgreSQL connection failed: {e}")
    logger.info("🔄 Falling back to SQLite...")
    
    # Fallback to SQLite
    engine = create_engine(
        SQLITE_FALLBACK,
        connect_args={"check_same_thread": False},
        echo=False
    )
    DB_TYPE = "sqlite"
    logger.info("✅ Connected to SQLite database (fallback)")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Initialize database tables
    """
    try:
        # Import models to register them
        from models import Base
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info(f"✅ Database tables created successfully ({DB_TYPE})")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def check_database_connection():
    """
    Check if database connection is working
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ Database connection check failed: {e}")
        return False

def get_database_info():
    """
    Get database information for health checks
    """
    return {
        "type": DB_TYPE,
        "url": DATABASE_URL if DB_TYPE == "postgresql" else SQLITE_FALLBACK,
        "connected": check_database_connection()
    }

# Health check function
async def database_health_check():
    """
    Async health check for database
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "type": DB_TYPE}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "type": DB_TYPE}
