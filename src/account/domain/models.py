from sqlalchemy import Boolean, Column, String

from src.shared.domain.base import Base


class Account(Base):
    email = Column[str](String, unique=True, index=True, nullable=False)
    hashed_password = Column[str](String, nullable=False)
    full_name = Column[str](String)
    is_active = Column[bool](Boolean, default=True)
    is_superuser = Column[bool](Boolean, default=False)
