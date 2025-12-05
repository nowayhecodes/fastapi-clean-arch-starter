from celery import Celery
from src.shared.infra.config import settings

celery_app = Celery(
    "fastapi-clean-arch-starter",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "src.account.application.tasks",
        "src.notification.application.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    worker_max_tasks_per_child=200,
    broker_connection_retry_on_startup=True,
) 