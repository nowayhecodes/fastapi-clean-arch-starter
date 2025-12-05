from sqlalchemy.orm import Session

from src.account.domain.models import Account
from src.account.domain.schemas import AccountCreate, AccountUpdate
from src.account.infra.repository import AccountRepository
from src.shared.application.crud_service import CRUDService


class AccountService(CRUDService[Account, AccountCreate, AccountUpdate]):
    def __init__(self):
        super().__init__(AccountRepository(Account))

    def get_by_email(self, db: Session, *, email: str) -> Account | None:
        return self.repository.get_by_email(db, email=email)

    def authenticate(self, db: Session, *, email: str, password: str) -> Account | None:
        return self.repository.authenticate(db, email=email, password=password)
