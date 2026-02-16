"""
Reports and analytics API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict
from datetime import datetime, timedelta

from ..core.database import get_db
from ..core.firebase_auth import get_current_user
from ..models.activity import Activity
from ..models.alert import Alert
from ..models.file_scan import FileScan

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary")
async def get_summary(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive security summary.

    Args:
        user: Authenticated user
        db: Database session

    Returns:
        Security summary dashboard data
    """
    # Activity stats
    total_activities = db.query(Activity).count()
    suspicious_activities = db.query(Activity).filter(
        Activity.is_suspicious == True
    ).count()

    # Alert stats
    total_alerts = db.query(Alert).count()
    active_alerts = db.query(Alert).filter(Alert.status == "active").count()
    critical_alerts = db.query(Alert).filter(
        Alert.severity == "critical",
        Alert.status == "active"
    ).count()

    # File scan stats
    total_scans = db.query(FileScan).count()
    malicious_files = db.query(FileScan).filter(
        FileScan.scan_result == "malicious"
    ).count()
    quarantined_files = db.query(FileScan).filter(
        FileScan.is_quarantined == True
    ).count()

    # Recent activities (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_activities = db.query(Activity).filter(
        Activity.timestamp >= yesterday
    ).count()

    recent_suspicious = db.query(Activity).filter(
        Activity.timestamp >= yesterday,
        Activity.is_suspicious == True
    ).count()

    # Activity by type
    activity_by_type = db.query(
        Activity.activity_type,
        func.count(Activity.id).label('count')
    ).group_by(Activity.activity_type).all()

    activity_type_data = {
        activity_type: count for activity_type, count in activity_by_type
    }

    # Alerts by severity
    alerts_by_severity = db.query(
        Alert.severity,
        func.count(Alert.id).label('count')
    ).group_by(Alert.severity).all()

    severity_data = {
        severity: count for severity, count in alerts_by_severity
    }

    # Timeline data (last 7 days)
    timeline_data = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        day_activities = db.query(Activity).filter(
            Activity.timestamp >= day_start,
            Activity.timestamp < day_end
        ).count()

        day_suspicious = db.query(Activity).filter(
            Activity.timestamp >= day_start,
            Activity.timestamp < day_end,
            Activity.is_suspicious == True
        ).count()

        timeline_data.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'activities': day_activities,
            'suspicious': day_suspicious
        })

    timeline_data.reverse()

    return {
        'overview': {
            'total_activities': total_activities,
            'suspicious_activities': suspicious_activities,
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'total_scans': total_scans,
            'malicious_files': malicious_files,
            'quarantined_files': quarantined_files,
        },
        'recent': {
            'activities_24h': recent_activities,
            'suspicious_24h': recent_suspicious,
        },
        'activity_by_type': activity_type_data,
        'alerts_by_severity': severity_data,
        'timeline': timeline_data,
    }


@router.get("/activities-timeline")
async def get_activities_timeline(
    days: int = 7,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activity timeline data.

    Args:
        days: Number of days to include
        user: Authenticated user
        db: Database session

    Returns:
        Timeline data
    """
    timeline = []

    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        total = db.query(Activity).filter(
            Activity.timestamp >= day_start,
            Activity.timestamp < day_end
        ).count()

        suspicious = db.query(Activity).filter(
            Activity.timestamp >= day_start,
            Activity.timestamp < day_end,
            Activity.is_suspicious == True
        ).count()

        timeline.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'total': total,
            'suspicious': suspicious,
            'safe': total - suspicious
        })

    timeline.reverse()
    return {'timeline': timeline}
