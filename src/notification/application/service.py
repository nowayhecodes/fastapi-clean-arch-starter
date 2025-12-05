from sqlalchemy.orm import Session

from src.notification.domain.models import Notification
from src.notification.domain.schemas import NotificationCreate, NotificationUpdate
from src.notification.infra.repository import NotificationRepository
from src.shared.application.crud_service import CRUDService


class NotificationService(
    CRUDService[Notification, NotificationCreate, NotificationUpdate]
):
    def __init__(self):
        super().__init__(NotificationRepository(Notification))

    def get_multi_by_account(
        self, db: Session, *, account_id: int, skip: int = 0, limit: int = 100
    ) -> list[Notification]:
        return self.repository.get_multi_by_account(
            db, account_id=account_id, skip=skip, limit=limit
        )

    def get_unread_count(self, db: Session, *, account_id: int) -> int:
        return self.repository.get_unread_count(db, account_id=account_id)
