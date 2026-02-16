"""
Threats and Alerts API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime

from ..core.database import get_db
from ..core.firebase_auth import get_current_user
from ..models.alert import Alert

router = APIRouter(prefix="/api/threats", tags=["threats"])


class AcknowledgeAlertRequest(BaseModel):
    """Request model for acknowledging an alert."""
    alert_id: int


@router.get("", response_model=List[Dict])
async def get_threats(
    limit: int = Query(100, ge=1, le=1000),
    severity: str = Query(None),
    status: str = Query(None),
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get security threats/alerts.

    Args:
        limit: Maximum number of alerts to return
        severity: Filter by severity (low, medium, high, critical)
        status: Filter by status (active, acknowledged, resolved)
        user: Authenticated user
        db: Database session

    Returns:
        List of alerts
    """
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity)

    if status:
        query = query.filter(Alert.status == status)

    alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()
    return [alert.to_dict() for alert in alerts]


@router.get("/stats", response_model=Dict)
async def get_threat_stats(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get threat statistics.

    Args:
        user: Authenticated user
        db: Database session

    Returns:
        Threat statistics
    """
    total_alerts = db.query(Alert).count()
    active_alerts = db.query(Alert).filter(Alert.status == "active").count()
    critical_alerts = db.query(Alert).filter(Alert.severity == "critical").count()

    # Count by severity
    severity_counts = {}
    for severity in ['low', 'medium', 'high', 'critical']:
        count = db.query(Alert).filter(Alert.severity == severity).count()
        severity_counts[severity] = count

    # Count by status
    status_counts = {}
    for status in ['active', 'acknowledged', 'resolved']:
        count = db.query(Alert).filter(Alert.status == status).count()
        status_counts[status] = count

    return {
        'total_alerts': total_alerts,
        'active_alerts': active_alerts,
        'critical_alerts': critical_alerts,
        'by_severity': severity_counts,
        'by_status': status_counts,
    }


@router.post("/acknowledge")
async def acknowledge_threat(
    request: AcknowledgeAlertRequest,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert.

    Args:
        request: Acknowledge request with alert_id
        user: Authenticated user
        db: Database session

    Returns:
        Updated alert
    """
    alert = db.query(Alert).filter(Alert.id == request.alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update alert status
    alert.status = "acknowledged"
    alert.acknowledged_by = user['email']
    alert.acknowledged_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)

    return {"success": True, "alert": alert.to_dict()}


@router.get("/{alert_id}", response_model=Dict)
async def get_threat(
    alert_id: int,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific alert by ID.

    Args:
        alert_id: Alert ID
        user: Authenticated user
        db: Database session

    Returns:
        Alert details
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert.to_dict()
