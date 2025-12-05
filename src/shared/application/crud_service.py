from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session
from src.shared.domain.repository import Repository
from src.shared.application.service import Service

T = TypeVar('T')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')

class CRUDService(Service[T, CreateSchemaType, UpdateSchemaType], Generic[T, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, repository: Repository[T]):
        self.repository = repository

    def get(self, db: Session, id: int) -> Optional[T]:
        return self.repository.get(db, id=id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[T]:
        return self.repository.get_multi(db, skip=skip, limit=limit)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> T:
        return self.repository.create(db, obj_in=obj_in)

    def update(self, db: Session, *, id: int, obj_in: UpdateSchemaType) -> T:
        db_obj = self.repository.get(db, id=id)
        return self.repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: int) -> T:
        return self.repository.remove(db, id=id) 