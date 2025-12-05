from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')

class Repository(Generic[T], ABC):
    @abstractmethod
    def get(self, db: Session, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[T]:
        pass

    @abstractmethod
    def create(self, db: Session, *, obj_in: T) -> T:
        pass

    @abstractmethod
    def update(self, db: Session, *, db_obj: T, obj_in: T) -> T:
        pass

    @abstractmethod
    def remove(self, db: Session, *, id: int) -> T:
        pass 