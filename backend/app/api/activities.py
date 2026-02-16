"""
Activities API endpoints.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from ..core.database import get_db
from ..core.firebase_auth import get_current_user
from ..services.activity_service import ActivityService
from ..models.activity import Activity

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("", response_model=List[Dict])
async def get_activities(
    limit: int = Query(100, ge=1, le=1000),
    suspicious_only: bool = Query(False),
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent activities.

    Args:
        limit: Maximum number of activities to return
        suspicious_only: Filter for suspicious activities only
        user: Authenticated user
        db: Database session

    Returns:
        List of activities
    """
    service = ActivityService(db)
    activities = service.get_activities(limit=limit, suspicious_only=suspicious_only)
    return [activity.to_dict() for activity in activities]


@router.get("/stats", response_model=Dict)
async def get_activity_stats(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activity statistics.

    Args:
        user: Authenticated user
        db: Database session

    Returns:
        Activity statistics
    """
    service = ActivityService(db)
    stats = service.get_activity_stats()
    return stats


@router.get("/{activity_id}", response_model=Dict)
async def get_activity(
    activity_id: int,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific activity by ID.

    Args:
        activity_id: Activity ID
        user: Authenticated user
        db: Database session

    Returns:
        Activity details
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Activity not found")

    return activity.to_dict()
