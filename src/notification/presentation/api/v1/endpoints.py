from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.shared.infra.database import get_db
from src.notification.application.service import NotificationService
from src.notification.domain.schemas import Notification, NotificationCreate, NotificationUpdate
from src.account.domain.schemas import Account

router = APIRouter()
notification_service = NotificationService()

@router.post("/", response_model=Notification)
def create_notification(
    *,
    db: Session = Depends(get_db),
    notification_in: NotificationCreate,
    current_account: Account = Depends(get_current_account),
) -> Any:
    if current_account.id != notification_in.account_id and not current_account.is_superuser:
        raise HTTPException(
            status_code=400,
            detail="Not enough permissions",
        )
    notification = notification_service.create(db, obj_in=notification_in)
    return notification

@router.get("/", response_model=List[Notification])
def read_notifications(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_account: Account = Depends(get_current_account),
) -> Any:
    notifications = notification_service.get_multi_by_account(
        db, account_id=current_account.id, skip=skip, limit=limit
    )
    return notifications

@router.get("/unread-count", response_model=int)
def read_unread_count(
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_account),
) -> Any:
    count = notification_service.get_unread_count(db, account_id=current_account.id)
    return count

@router.put("/{notification_id}", response_model=Notification)
def update_notification(
    *,
    db: Session = Depends(get_db),
    notification_id: int,
    notification_in: NotificationUpdate,
    current_account: Account = Depends(get_current_account),
) -> Any:
    notification = notification_service.get(db, id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.account_id != current_account.id and not current_account.is_superuser:
        raise HTTPException(
            status_code=400,
            detail="Not enough permissions",
        )
    notification = notification_service.update(
        db, db_obj=notification, obj_in=notification_in
    )
    return notification 