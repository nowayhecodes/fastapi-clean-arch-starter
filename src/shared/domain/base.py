from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(self, cls) -> str:
        return cls.__name__.lower()

    id = Column[int](Integer, primary_key=True, index=True)
    created_at = Column[datetime](
        DateTime, default=datetime.now(datetime.timezone.utc), nullable=False
    )
    updated_at = Column[datetime](
        DateTime,
        default=datetime.now(datetime.timezone.utc),
        onupdate=datetime.now(datetime.timezone.utc),
        nullable=False,
    )
