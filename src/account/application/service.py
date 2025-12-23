"""Account service with business logic.

This service implements the business logic for account management,
following the Dependency Inversion Principle by depending on the
repository abstraction rather than concrete implementation.
"""
from sqlalchemy.orm import Session

from src.account.domain.models import Account
from src.account.domain.schemas import AccountCreate, AccountUpdate
from src.account.infra.repository import AccountRepository
from src.shared.application.crud_service import CRUDService


class AccountService(CRUDService[Account, AccountCreate, AccountUpdate]):
    """Account service for managing account operations.
    
    This service receives its dependencies through constructor injection,
    following the Dependency Inversion Principle.
    """
    
    def __init__(self, repository: AccountRepository):
        """Initialize service with injected repository.
        
        Args:
            repository: Account repository instance (injected).
        """
        super().__init__(repository)

    def get_by_email(self, db: Session, *, email: str) -> Account | None:
        """Get account by email address.
        
        Args:
            db: Database session.
            email: Email address to search for.
            
        Returns:
            Account if found, None otherwise.
        """
        return self.repository.get_by_email(db, email=email)

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Account | None:
        """Authenticate user with email and password.
        
        Args:
            db: Database session.
            email: User's email address.
            password: User's password (plain text).
            
        Returns:
            Account if authentication successful, None otherwise.
        """
        return self.repository.authenticate(db, email=email, password=password)
