from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class Service(Generic[T, CreateSchemaType, UpdateSchemaType], ABC):
    @abstractmethod
    def get(self, db: Session, id: int) -> T | None:
        pass

    @abstractmethod
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[T]:
        pass

    @abstractmethod
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> T:
        pass

    @abstractmethod
    def update(self, db: Session, *, id: int, obj_in: UpdateSchemaType) -> T:
        pass

    @abstractmethod
    def remove(self, db: Session, *, id: int) -> T:
        pass
