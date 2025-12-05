from celery import shared_task

from src.notification.application.service import NotificationService
from src.notification.domain.schemas import NotificationCreate
from src.shared.infra.database import SessionLocal

notification_service = NotificationService()


@shared_task
def send_notification(account_id: int, title: str, message: str):
    db = SessionLocal()
    try:
        notification_in = NotificationCreate(
            account_id=account_id,
            title=title,
            message=message,
        )
        notification_service.create(db, obj_in=notification_in)
    finally:
        db.close()
