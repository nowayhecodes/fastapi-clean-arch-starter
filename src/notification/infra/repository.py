from sqlalchemy.orm import Session

from src.notification.domain.models import Notification
from src.notification.domain.schemas import NotificationCreate, NotificationUpdate
from src.shared.infra.cache import cache_manager
from src.shared.infra.repository import CRUDRepository


class NotificationRepository(
    CRUDRepository[Notification, NotificationCreate, NotificationUpdate]
):
    def __init__(self, model: type[Notification]):
        super().__init__(model)
        self.cache_prefix = "notification:"

    async def get_multi_by_account(
        self, db: Session, *, account_id: int, skip: int = 0, limit: int = 100
    ) -> list[Notification]:
        cache_key = f"{self.cache_prefix}account:{account_id}:{skip}:{limit}"
        cached_notifications = await cache_manager.get(cache_key)
        if cached_notifications:
            return [Notification(**n) for n in cached_notifications]

        notifications = (
            db.query(Notification)
            .filter(Notification.account_id == account_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

        if notifications:
            await cache_manager.set(cache_key, [n.__dict__ for n in notifications])

        return notifications

    async def get_unread_count(self, db: Session, *, account_id: int) -> int:
        cache_key = f"{self.cache_prefix}unread:{account_id}"
        cached_count = await cache_manager.get(cache_key)
        if cached_count is not None:
            return cached_count

        count = (
            db.query(Notification)
            .filter(
                Notification.account_id == account_id, Notification.is_read is not False
            )
            .count()
        )

        await cache_manager.set(cache_key, count, expire=60)  # Cache for 1 minute

        return count

    async def create(self, db: Session, *, obj_in: NotificationCreate) -> Notification:
        db_obj = Notification(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Clear account-specific caches
        await cache_manager.clear_pattern(
            f"{self.cache_prefix}account:{db_obj.account_id}:*"
        )
        await cache_manager.delete(f"{self.cache_prefix}unread:{db_obj.account_id}")

        return db_obj

    async def update(
        self, db: Session, *, db_obj: Notification, obj_in: NotificationUpdate
    ) -> Notification:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Clear account-specific caches
        await cache_manager.clear_pattern(
            f"{self.cache_prefix}account:{db_obj.account_id}:*"
        )
        await cache_manager.delete(f"{self.cache_prefix}unread:{db_obj.account_id}")

        return db_obj

    async def remove(self, db: Session, *, id: int) -> Notification:
        notification = await self.get(db, id=id)
        if notification:
            await db.delete(notification)
            await db.commit()

            # Clear account-specific caches
            await cache_manager.clear_pattern(
                f"{self.cache_prefix}account:{notification.account_id}:*"
            )
            await cache_manager.delete(
                f"{self.cache_prefix}unread:{notification.account_id}"
            )

        return notification
