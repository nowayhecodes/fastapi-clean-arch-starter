from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.shared.infra.database import get_db
from src.account.application.service import AccountService
from src.account.domain.schemas import Account, AccountCreate, AccountUpdate

router = APIRouter()
account_service = AccountService()

@router.post("/", response_model=Account)
def create_account(
    *,
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_account),
) -> Any:
    return current_account

@router.post("/login")
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
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