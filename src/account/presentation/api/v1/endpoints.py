from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.account.application.service import AccountService
from src.account.domain.schemas import Account, AccountCreate
from src.shared.infra.database import get_db

router = APIRouter()
account_service = AccountService()

# Module-level dependency instances to avoid Ruff B008 warning
_get_db = Depends(get_db)
_get_oauth2_form = Depends()


def get_current_account(db: Annotated[Session, Depends(get_db)]) -> Account:
    """Get current authenticated account.

    TODO: Implement proper JWT token validation to get the current user.
    This is a placeholder that needs proper authentication implementation.
    """
    # TODO: Extract user from JWT token and return the account
    raise HTTPException(status_code=401, detail="Not authenticated")


_get_current_account = Depends(get_current_account)


@router.post("/", response_model=Account)
def create_account(
    *,
    db: Session = _get_db,
    account_in: AccountCreate,
) -> Any:
    account = account_service.get_by_email(db, email=account_in.email)
    if account:
        raise HTTPException(
            status_code=400,
            detail="The account with this email already exists in the system.",
        )
    account = account_service.create(db, obj_in=account_in)
    return account


@router.get("/me", response_model=Account)
def read_account_me(
    current_account: Account = _get_current_account,
) -> Any:
    return current_account


@router.post("/login")
def login(
    db: Session = _get_db,
    form_data: OAuth2PasswordRequestForm = _get_oauth2_form,
) -> Any:
    account = account_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not account:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not account.is_active:
        raise HTTPException(status_code=400, detail="Inactive account")
    # TODO: Return access token
    return {"access_token": "dummy_token", "token_type": "bearer"}
