from celery import shared_task
from sqlalchemy.orm import Session
from src.shared.infra.database import SessionLocal
from src.account.application.service import AccountService
from src.notification.application.tasks import send_notification

account_service = AccountService()

@shared_task
def send_welcome_email(account_id: int):
    db = SessionLocal()
    try:
        account = account_service.get(db, id=account_id)
        if account:
            send_notification.delay(
                account_id=account.id,
                title="Welcome to FastAPI Clean Arch Starter",
                message=f"Welcome {account.full_name}! We're glad to have you on board.",
            )
    finally:
        db.close() 