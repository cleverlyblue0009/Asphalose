"""
Script to train ML models.
Run this script to train and save both behavioral classifier and anomaly detector.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ml.behavioral_classifier import BehavioralClassifier
from app.ml.anomaly_detector import AnomalyDetector
from app.core.config import settings


def train_behavioral_classifier():
    """Train and save the behavioral classification model."""
    print("\n" + "="*60)
    print("TRAINING BEHAVIORAL CLASSIFIER")
    print("="*60)

    classifier = BehavioralClassifier()
    metrics = classifier.train()

    # Save model
    model_path = os.path.join(settings.MODEL_PATH, 'behavioral_classifier.joblib')
    classifier.save_model(model_path)

    return metrics


def train_anomaly_detector():
    """Train and save the anomaly detection model."""
    print("\n" + "="*60)
    print("TRAINING ANOMALY DETECTOR")
    print("="*60)

    detector = AnomalyDetector()
    metrics = detector.train()

    # Save model
    model_path = os.path.join(settings.MODEL_PATH, 'anomaly_detector.joblib')
    detector.save_model(model_path)

    return metrics


def main():
    """Main training function."""
    print("\n🤖 AI Threat Detection System - Model Training")
    print("=" * 60)

    # Train behavioral classifier
    bc_metrics = train_behavioral_classifier()

    # Train anomaly detector
    ad_metrics = train_anomaly_detector()

    # Summary
    print("\n" + "="*60)
    print("TRAINING SUMMARY")
    print("="*60)
    print("\n✓ Behavioral Classifier:")
    print(f"  - Accuracy: {bc_metrics['accuracy']:.3f}")
    print(f"  - F1 Score: {bc_metrics['f1_score']:.3f}")
    print(f"  - Training time: {bc_metrics['training_duration']:.2f}s")

    print("\n✓ Anomaly Detector:")
    print(f"  - Anomaly rate: {ad_metrics['anomaly_percentage']:.1f}%")
    print(f"  - Training samples: {ad_metrics['training_samples']}")

    print("\n✓ Models saved to:", settings.MODEL_PATH)
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
