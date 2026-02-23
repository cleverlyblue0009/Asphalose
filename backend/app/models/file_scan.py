"""
FileScan model for storing file scanning results.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, BigInteger
from sqlalchemy.sql import func
from ..core.database import Base


class FileScan(Base):
    """File scan result model."""

    __tablename__ = "file_scans"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(100), nullable=True)
    scan_result = Column(String(20), nullable=False, index=True)  # safe, suspicious, malicious
    confidence_score = Column(Float, nullable=True)
    is_quarantined = Column(Boolean, default=False)
    quarantine_path = Column(Text, nullable=True)
    scanned_by = Column(String(100), nullable=True)
    scan_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "scan_result": self.scan_result,
            "confidence_score": self.confidence_score,
            "is_quarantined": self.is_quarantined,
            "quarantine_path": self.quarantine_path,
            "scanned_by": self.scanned_by,
            "scan_timestamp": self.scan_timestamp.isoformat() if self.scan_timestamp else None,
            "extra_data": self.extra_data,
        }
