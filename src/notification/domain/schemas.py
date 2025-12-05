from datetime import datetime

from pydantic import BaseModel


class NotificationBase(BaseModel):
    title: str
    message: str
    account_id: int


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: bool | None = None


class NotificationInDBBase(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Notification(NotificationInDBBase):
    pass
