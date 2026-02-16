"""
Activity model for storing system activities and events.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.sql import func
from ..core.database import Base


class Activity(Base):
    """System activity log model."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # process, file_access, login, network
    description = Column(Text, nullable=False)
    source_ip = Column(String(45), nullable=True)
    user_id = Column(String(100), nullable=True)
    process_name = Column(String(255), nullable=True)
    file_path = Column(Text, nullable=True)
    is_suspicious = Column(Boolean, default=False, index=True)
    confidence_score = Column(Float, nullable=True)  # ML model confidence
    severity = Column(String(20), nullable=True)  # low, medium, high, critical
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "activity_type": self.activity_type,
            "description": self.description,
            "source_ip": self.source_ip,
            "user_id": self.user_id,
            "process_name": self.process_name,
            "file_path": self.file_path,
            "is_suspicious": self.is_suspicious,
            "confidence_score": self.confidence_score,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata,
        }
