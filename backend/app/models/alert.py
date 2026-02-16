"""
Alert model for storing security alerts and threats.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from ..core.database import Base


class Alert(Base):
    """Security alert model."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # malware, suspicious_activity, anomaly
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    status = Column(String(20), default="active", index=True)  # active, acknowledged, resolved
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    file_scan_id = Column(Integer, ForeignKey("file_scans.id"), nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    metadata = Column(Text, nullable=True)  # JSON string for additional data

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "activity_id": self.activity_id,
            "file_scan_id": self.file_scan_id,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
        }
