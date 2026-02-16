"""
Celery application configuration.
"""
from celery import Celery
from ..core.config import settings

# Create Celery app
celery_app = Celery(
    "threat_detection",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=4,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "generate-activities": {
        "task": "app.workers.tasks.generate_activity_task",
        "schedule": float(settings.ACTIVITY_GENERATION_INTERVAL),
    },
}
