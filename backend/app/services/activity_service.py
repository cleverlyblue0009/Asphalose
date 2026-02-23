"""
Activity monitoring and analysis service.
"""
import os
import random
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.activity import Activity
from ..models.alert import Alert
from ..ml.behavioral_classifier import BehavioralClassifier
from ..ml.anomaly_detector import AnomalyDetector
from ..core.config import settings


class ActivityService:
    """Service for managing and analyzing activities."""

    def __init__(self, db: Session):
        """
        Initialize activity service.

        Args:
            db: Database session
        """
        self.db = db

        # Load ML models
        classifier_path = os.path.join(settings.MODEL_PATH, 'behavioral_classifier.joblib')
        anomaly_path = os.path.join(settings.MODEL_PATH, 'anomaly_detector.joblib')

        try:
            self.classifier = BehavioralClassifier(classifier_path)
        except:
            print("Warning: Could not load behavioral classifier")
            self.classifier = None

        try:
            self.anomaly_detector = AnomalyDetector(anomaly_path)
        except:
            print("Warning: Could not load anomaly detector")
            self.anomaly_detector = None

    def analyze_activity(self, activity_data: Dict) -> tuple[bool, float, str]:
        """
        Analyze activity using ML models.

        Args:
            activity_data: Activity features

        Returns:
            Tuple of (is_suspicious, confidence, severity)
        """
        # Extract features for ML models
        features = {
            'activity_type': activity_data.get('activity_type', 'unknown'),
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            'process_count': activity_data.get('process_count', 5),
            'file_access_count': activity_data.get('file_access_count', 10),
            'network_connection_count': activity_data.get('network_connection_count', 3),
            'failed_login_attempts': activity_data.get('failed_login_attempts', 0),
            'cpu_usage': activity_data.get('cpu_usage', 40),
            'memory_usage': activity_data.get('memory_usage', 50),
            'disk_io_count': activity_data.get('disk_io_count', 20),
        }

        is_suspicious = False
        confidence = 0.5
        severity = 'low'

        # Behavioral classification
        if self.classifier:
            try:
                is_suspicious_bc, conf_bc = self.classifier.predict(features)
                if is_suspicious_bc and conf_bc > settings.ML_CONFIDENCE_THRESHOLD:
                    is_suspicious = True
                    confidence = max(confidence, conf_bc)
            except Exception as e:
                print(f"Behavioral classification error: {e}")

        # Anomaly detection
        if self.anomaly_detector:
            try:
                is_anomaly, conf_ad = self.anomaly_detector.predict(features)
                if is_anomaly and conf_ad > settings.ML_CONFIDENCE_THRESHOLD:
                    is_suspicious = True
                    confidence = max(confidence, conf_ad)
            except Exception as e:
                print(f"Anomaly detection error: {e}")

        # Determine severity
        if is_suspicious:
            if confidence > 0.9:
                severity = 'critical'
            elif confidence > 0.8:
                severity = 'high'
            elif confidence > 0.7:
                severity = 'medium'
            else:
                severity = 'low'

        return is_suspicious, confidence, severity

    def create_activity(self, activity_data: Dict) -> Activity:
        """
        Create and analyze a new activity.

        Args:
            activity_data: Activity data

        Returns:
            Created activity
        """
        # Analyze activity
        is_suspicious, confidence, severity = self.analyze_activity(activity_data)

        # Create activity record
        activity = Activity(
            activity_type=activity_data.get('activity_type'),
            description=activity_data.get('description'),
            source_ip=activity_data.get('source_ip'),
            user_id=activity_data.get('user_id'),
            process_name=activity_data.get('process_name'),
            file_path=activity_data.get('file_path'),
            is_suspicious=is_suspicious,
            confidence_score=confidence if is_suspicious else None,
            severity=severity if is_suspicious else None,
            extra_data=activity_data.get('extra_data'),
        )

        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)

        # Create alert if suspicious
        if is_suspicious and confidence > settings.ML_CONFIDENCE_THRESHOLD:
            alert = Alert(
                alert_type='suspicious_activity',
                title=f"Suspicious {activity_data.get('activity_type')} detected",
                description=f"{activity_data.get('description')} (Confidence: {confidence:.2%})",
                severity=severity,
                activity_id=activity.id,
            )
            self.db.add(alert)
            self.db.commit()

        return activity

    def get_activities(
        self,
        limit: int = 100,
        suspicious_only: bool = False
    ) -> List[Activity]:
        """
        Get recent activities.

        Args:
            limit: Maximum number of activities
            suspicious_only: Filter for suspicious activities only

        Returns:
            List of activities
        """
        query = self.db.query(Activity)

        if suspicious_only:
            query = query.filter(Activity.is_suspicious == True)

        activities = query.order_by(desc(Activity.timestamp)).limit(limit).all()
        return activities

    def get_activity_stats(self) -> Dict:
        """
        Get activity statistics.

        Returns:
            Dictionary of statistics
        """
        total_activities = self.db.query(Activity).count()
        suspicious_count = self.db.query(Activity).filter(
            Activity.is_suspicious == True
        ).count()

        # Count by type
        activity_types = self.db.query(
            Activity.activity_type,
            Activity.is_suspicious
        ).all()

        type_counts = {}
        for act_type, is_susp in activity_types:
            if act_type not in type_counts:
                type_counts[act_type] = {'total': 0, 'suspicious': 0}
            type_counts[act_type]['total'] += 1
            if is_susp:
                type_counts[act_type]['suspicious'] += 1

        return {
            'total_activities': total_activities,
            'suspicious_count': suspicious_count,
            'safe_count': total_activities - suspicious_count,
            'by_type': type_counts,
        }


def generate_fake_activity() -> Dict:
    """
    Generate fake activity data for demonstration.

    Returns:
        Dictionary of activity data
    """
    activity_types = [
        {
            'type': 'process',
            'descriptions': [
                'System process started',
                'Background service initiated',
                'User application launched',
                'Scheduled task executed',
            ]
        },
        {
            'type': 'file_access',
            'descriptions': [
                'File read operation',
                'File write operation',
                'File deleted',
                'File permissions changed',
            ]
        },
        {
            'type': 'login',
            'descriptions': [
                'Successful login',
                'Failed login attempt',
                'User logged out',
                'Session expired',
            ]
        },
        {
            'type': 'network',
            'descriptions': [
                'Outbound connection established',
                'Inbound connection received',
                'Data transfer completed',
                'Connection timeout',
            ]
        },
    ]

    # Select random activity type
    activity = random.choice(activity_types)
    activity_type = activity['type']
    description = random.choice(activity['descriptions'])

    # Generate random features
    data = {
        'activity_type': activity_type,
        'description': description,
        'source_ip': f"192.168.1.{random.randint(1, 254)}",
        'user_id': f"user_{random.randint(1, 100)}",
        'process_name': f"process_{random.randint(1, 50)}.exe" if activity_type == 'process' else None,
        'file_path': f"/path/to/file_{random.randint(1, 1000)}.txt" if activity_type == 'file_access' else None,
        'process_count': random.randint(1, 30),
        'file_access_count': random.randint(1, 50),
        'network_connection_count': random.randint(1, 20),
        'failed_login_attempts': random.randint(0, 5) if activity_type == 'login' else 0,
        'cpu_usage': random.uniform(10, 90),
        'memory_usage': random.uniform(20, 85),
        'disk_io_count': random.randint(5, 100),
    }

    return data
