"""
ModelMetrics model for storing ML model performance metrics.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from ..core.database import Base


class ModelMetrics(Base):
    """ML model performance metrics model."""

    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    model_type = Column(String(50), nullable=False)  # classification, anomaly_detection
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    training_samples = Column(Integer, nullable=True)
    training_duration = Column(Float, nullable=True)  # seconds
    model_version = Column(String(50), nullable=True)
    trained_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "model_name": self.model_name,
            "model_type": self.model_type,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "training_samples": self.training_samples,
            "training_duration": self.training_duration,
            "model_version": self.model_version,
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "metadata": self.metadata,
        }
