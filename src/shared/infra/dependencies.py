"""Dependency injection container and providers.

This module implements a proper dependency injection system following
the Inversion of Control (IoC) principle, ensuring loose coupling between
layers and making the application more testable and maintainable.
"""
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infra.database import get_db


# Database session dependency
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with proper cleanup.
    
    This is the primary dependency for database access.
    All repositories and services should use this.
    
    Yields:
        AsyncSession: Database session.
    """
    async for session in get_db():
        yield session


# Type alias for cleaner annotations
DatabaseSession = Annotated[AsyncSession, Depends(get_database_session)]

