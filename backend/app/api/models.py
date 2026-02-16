"""
ML Models API endpoints.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict
import os

from ..core.database import get_db
from ..core.firebase_auth import get_current_user
from ..models.model_metrics import ModelMetrics
from ..ml.behavioral_classifier import BehavioralClassifier
from ..ml.anomaly_detector import AnomalyDetector
from ..core.config import settings

router = APIRouter(prefix="/api/models", tags=["models"])


def train_models_background(db_session):
    """Background task to train models."""
    try:
        # Train behavioral classifier
        classifier = BehavioralClassifier()
        bc_metrics = classifier.train()

        # Save model
        bc_path = os.path.join(settings.MODEL_PATH, 'behavioral_classifier.joblib')
        classifier.save_model(bc_path)

        # Save metrics to database
        bc_model_metrics = ModelMetrics(
            model_name='behavioral_classifier',
            model_type='classification',
            accuracy=bc_metrics['accuracy'],
            precision=bc_metrics['precision'],
            recall=bc_metrics['recall'],
            f1_score=bc_metrics['f1_score'],
            training_samples=bc_metrics['training_samples'],
            training_duration=bc_metrics['training_duration'],
            model_version='1.0'
        )
        db_session.add(bc_model_metrics)

        # Train anomaly detector
        detector = AnomalyDetector()
        ad_metrics = detector.train()

        # Save model
        ad_path = os.path.join(settings.MODEL_PATH, 'anomaly_detector.joblib')
        detector.save_model(ad_path)

        # Save metrics to database
        ad_model_metrics = ModelMetrics(
            model_name='anomaly_detector',
            model_type='anomaly_detection',
            training_samples=ad_metrics['training_samples'],
            training_duration=0,
            model_version='1.0'
        )
        db_session.add(ad_model_metrics)

        db_session.commit()
        print("✓ Models trained and saved successfully")

    except Exception as e:
        print(f"Error training models: {e}")
        db_session.rollback()
    finally:
        db_session.close()


@router.post("/train")
async def train_models(
    background_tasks: BackgroundTasks,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger model training.

    Args:
        background_tasks: FastAPI background tasks
        user: Authenticated user
        db: Database session

    Returns:
        Training status
    """
    # Create new session for background task
    from ..core.database import SessionLocal
    db_session = SessionLocal()

    # Start training in background
    background_tasks.add_task(train_models_background, db_session)

    return {
        "success": True,
        "message": "Model training started in background"
    }


@router.get("/metrics")
async def get_model_metrics(
    limit: int = 10,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get model performance metrics.

    Args:
        limit: Maximum number of metrics to return
        user: Authenticated user
        db: Database session

    Returns:
        List of model metrics
    """
    metrics = db.query(ModelMetrics).order_by(
        desc(ModelMetrics.trained_at)
    ).limit(limit).all()

    return [metric.to_dict() for metric in metrics]


@router.get("/metrics/latest")
async def get_latest_metrics(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get latest metrics for each model.

    Args:
        user: Authenticated user
        db: Database session

    Returns:
        Latest metrics for each model
    """
    # Get latest behavioral classifier metrics
    bc_metrics = db.query(ModelMetrics).filter(
        ModelMetrics.model_name == 'behavioral_classifier'
    ).order_by(desc(ModelMetrics.trained_at)).first()

    # Get latest anomaly detector metrics
    ad_metrics = db.query(ModelMetrics).filter(
        ModelMetrics.model_name == 'anomaly_detector'
    ).order_by(desc(ModelMetrics.trained_at)).first()

    return {
        'behavioral_classifier': bc_metrics.to_dict() if bc_metrics else None,
        'anomaly_detector': ad_metrics.to_dict() if ad_metrics else None,
    }


@router.get("/status")
async def get_model_status(
    user: Dict = Depends(get_current_user)
):
    """
    Check if models are trained and available.

    Args:
        user: Authenticated user

    Returns:
        Model availability status
    """
    bc_path = os.path.join(settings.MODEL_PATH, 'behavioral_classifier.joblib')
    ad_path = os.path.join(settings.MODEL_PATH, 'anomaly_detector.joblib')

    bc_exists = os.path.exists(bc_path)
    ad_exists = os.path.exists(ad_path)

    return {
        'behavioral_classifier': {
            'available': bc_exists,
            'path': bc_path
        },
        'anomaly_detector': {
            'available': ad_exists,
            'path': ad_path
        },
        'all_ready': bc_exists and ad_exists
    }
