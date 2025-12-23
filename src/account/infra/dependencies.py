"""Dependency injection providers for the account module.

This module provides FastAPI dependency functions for injecting
repositories and services into route handlers.
"""
from typing import Annotated

from fastapi import Depends

from src.account.application.service import AccountService
from src.account.domain.models import Account
from src.account.infra.repository import AccountRepository
from src.shared.infra.dependencies import DatabaseSession


def get_account_repository() -> AccountRepository:
    """Get account repository instance.
    
    Returns:
        AccountRepository instance.
    """
    return AccountRepository(Account)


def get_account_service(
    repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> AccountService:
    """Get account service instance with injected repository.
    
    Args:
        repository: Injected account repository.
        
    Returns:
        AccountService instance.
    """
    return AccountService(repository)


# Type aliases for cleaner annotations in route handlers
AccountRepositoryDep = Annotated[AccountRepository, Depends(get_account_repository)]
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]

