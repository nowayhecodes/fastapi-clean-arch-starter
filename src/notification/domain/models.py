from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.shared.domain.base import Base


class Notification(Base):
    title = Column[str](String, nullable=False)
    message = Column[str](Text, nullable=False)
    is_read = Column[bool](Boolean, default=False)
    account_id = Column[int](Integer, ForeignKey("account.id"), nullable=False)
    account = relationship("Account", back_populates="notifications")
