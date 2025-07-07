from sqlalchemy import Column, Integer, DateTime, func, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields for all entities."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def update_from_dict(self, data: dict):
        """Update model from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class AuditLogModel(object):
    """Base model with audit logging capabilities."""
    
    __abstract__ = True
    
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def soft_delete(self, user_id: str = None):
        """Soft delete the record."""
        self.is_active = False
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()
    
    def activate(self, user_id: str = None):
        """Activate the record."""
        self.is_active = True
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()


class SyncLogModel(object):
    """Model for tracking synchronization operations."""
    
    __abstract__ = True
    
    sync_status = Column(String(50), default="pending")  # pending, success, failed
    sync_attempts = Column(Integer, default=0)
    last_sync_at = Column(DateTime, nullable=True)
    sync_error = Column(Text, nullable=True)
    
    def mark_sync_success(self):
        """Mark synchronization as successful."""
        self.sync_status = "success"
        self.last_sync_at = datetime.utcnow()
        self.sync_error = None
    
    def mark_sync_failed(self, error: str):
        """Mark synchronization as failed."""
        self.sync_status = "failed"
        self.sync_attempts += 1
        self.sync_error = error
        self.last_sync_at = datetime.utcnow()
