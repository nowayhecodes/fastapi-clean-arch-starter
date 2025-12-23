"""Account API endpoints with proper dependency injection.

This module demonstrates proper dependency injection using FastAPI's
Depends() system. Services and repositories are injected per-request,
ensuring proper lifecycle management and testability.
"""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.account.application.service import AccountService
from src.account.domain.schemas import Account, AccountCreate
from src.account.infra.dependencies import AccountServiceDep
from src.shared.infra.dependencies import DatabaseSession

router = APIRouter()


def get_current_account(
    db: DatabaseSession,
    service: AccountServiceDep,
) -> Account:
    """Get current authenticated account.

    TODO: Implement proper JWT token validation to get the current user.
    This is a placeholder that needs proper authentication implementation.
    
    Args:
        db: Database session (injected).
        service: Account service (injected).
        
    Returns:
        Current authenticated account.
        
    Raises:
        HTTPException: If not authenticated.
    """
    # TODO: Extract user from JWT token and return the account
    raise HTTPException(status_code=401, detail="Not authenticated")


CurrentAccountDep = Annotated[Account, Depends(get_current_account)]


@router.post("/", response_model=Account)
async def create_account(
    *,
    db: DatabaseSession,
    service: AccountServiceDep,
    account_in: AccountCreate,
) -> Any:
    """Create a new account.
    
    Args:
        db: Database session (injected).
        service: Account service (injected).
        account_in: Account creation data.
        
    Returns:
        Created account.
        
    Raises:
        HTTPException: If account with email already exists.
    """
    account = await service.get_by_email(db, email=account_in.email)
    if account:
        raise HTTPException(
            status_code=400,
            detail="The account with this email already exists in the system.",
        )
    account = await service.create(db, obj_in=account_in)
    return account


@router.get("/me", response_model=Account)
async def read_account_me(
    current_account: CurrentAccountDep,
) -> Any:
    """Get current account information.
    
    Args:
        current_account: Current authenticated account (injected).
        
    Returns:
        Current account information.
    """
    return current_account


@router.post("/login")
async def login(
    db: DatabaseSession,
    service: AccountServiceDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    """Authenticate user and return access token.
    
    Args:
        db: Database session (injected).
        service: Account service (injected).
        form_data: OAuth2 form data with username and password.
        
    Returns:
        Access token and token type.
        
    Raises:
        HTTPException: If authentication fails.
    """
    account = await service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not account:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not account.is_active:
        raise HTTPException(status_code=400, detail="Inactive account")
    # TODO: Return access token
    return {"access_token": "dummy_token", "token_type": "bearer"}
