#!/usr/bin/env python3
"""
Database initialization script for SEARCB
"""
import os
import sys
import logging
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import after path is set
from app.core.database import engine, Base
from app.models import *  # Import all models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # List tables to confirm
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Created tables: {tables}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    if not success:
        sys.exit(1)