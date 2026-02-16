"""
Celery background tasks.
"""
from .celery_app import celery_app
from ..core.database import SessionLocal
from ..services.activity_service import ActivityService, generate_fake_activity


@celery_app.task(name="app.workers.tasks.generate_activity_task")
def generate_activity_task():
    """
    Periodic task to generate fake activities for demonstration.
    This simulates real-time system monitoring.
    """
    db = SessionLocal()
    try:
        # Generate fake activity
        activity_data = generate_fake_activity()

        # Create and analyze activity
        service = ActivityService(db)
        activity = service.create_activity(activity_data)

        return {
            "success": True,
            "activity_id": activity.id,
            "is_suspicious": activity.is_suspicious,
        }
    except Exception as e:
        print(f"Error generating activity: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.analyze_activity_batch")
def analyze_activity_batch(activity_ids: list):
    """
    Batch analyze multiple activities.

    Args:
        activity_ids: List of activity IDs to analyze
    """
    db = SessionLocal()
    try:
        service = ActivityService(db)
        results = []

        for activity_id in activity_ids:
            # Re-analyze activity
            activity = db.query(Activity).get(activity_id)
            if activity:
                # Convert to dict for analysis
                activity_data = activity.to_dict()
                is_suspicious, confidence, severity = service.analyze_activity(activity_data)

                # Update activity
                activity.is_suspicious = is_suspicious
                activity.confidence_score = confidence
                activity.severity = severity

                results.append({
                    "activity_id": activity_id,
                    "is_suspicious": is_suspicious,
                    "confidence": confidence
                })

        db.commit()
        return {"success": True, "results": results}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()
