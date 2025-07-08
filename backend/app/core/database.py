from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import logging
from typing import Generator

from .config import settings

# Import models to ensure they're registered with Base
from ..models import *

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency to get database session.
    Yields database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    except ValidationError as e:
        logger.warning(f"Validation error in database operation: {str(e)}")
        db.rollback()
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error ({type(e).__name__}): {str(e)}", exc_info=True)
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database operation: {type(e).__name__}: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def check_db_connection():
    """Check database connection health."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
