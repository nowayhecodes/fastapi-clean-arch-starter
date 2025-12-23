"""Database configuration with multi-schema tenant support."""
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from src.shared.domain.base import Base
from src.shared.infra.config import settings
from src.shared.infra.tenant_context import get_current_tenant_id

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://"),
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    # Isolation level for proper schema switching
    isolation_level="READ COMMITTED",
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with tenant schema context.
    
    This function creates a database session and sets the PostgreSQL search_path
    to the tenant's schema, ensuring data isolation between tenants.
    
    Yields:
        AsyncSession: Database session configured for the current tenant.
        
    Raises:
        ValueError: If no tenant ID is found in the context.
    """
    tenant_id = get_current_tenant_id()
    
    if not tenant_id:
        raise ValueError(
            "Tenant ID not found in context. "
            "Ensure TenantMiddleware is properly configured."
        )
    
    async with AsyncSessionLocal() as session:
        try:
            # Set the search_path to the tenant's schema
            # This ensures all queries are executed in the tenant's schema
            schema_name = f"tenant_{tenant_id}"
            await session.execute(text(f"SET search_path TO {schema_name}, public"))
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database by creating tables in the public schema.
    
    This creates the base table structure. Individual tenant schemas
    should be created separately using create_tenant_schema().
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_tenant_schema(tenant_id: str) -> None:
    """Create a new schema for a tenant and initialize all tables.
    
    Args:
        tenant_id: The tenant identifier.
        
    Raises:
        ValueError: If tenant_id format is invalid.
    """
    if not tenant_id.replace("_", "").isalnum():
        raise ValueError("Invalid tenant ID format")
    
    schema_name = f"tenant_{tenant_id}"
    
    async with engine.begin() as conn:
        # Create schema if it doesn't exist
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        
        # Set search_path to the new schema
        await conn.execute(text(f"SET search_path TO {schema_name}, public"))
        
        # Create all tables in the tenant schema
        await conn.run_sync(Base.metadata.create_all)


async def drop_tenant_schema(tenant_id: str, cascade: bool = True) -> None:
    """Drop a tenant's schema and all its data.
    
    WARNING: This permanently deletes all data for the tenant.
    
    Args:
        tenant_id: The tenant identifier.
        cascade: If True, drops all objects in the schema. Defaults to True.
        
    Raises:
        ValueError: If tenant_id format is invalid.
    """
    if not tenant_id.replace("_", "").isalnum():
        raise ValueError("Invalid tenant ID format")
    
    schema_name = f"tenant_{tenant_id}"
    cascade_clause = "CASCADE" if cascade else "RESTRICT"
    
    async with engine.begin() as conn:
        await conn.execute(
            text(f"DROP SCHEMA IF EXISTS {schema_name} {cascade_clause}")
        )


async def list_tenant_schemas() -> list[str]:
    """List all tenant schemas in the database.
    
    Returns:
        List of tenant IDs (without the 'tenant_' prefix).
    """
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name LIKE 'tenant_%'"
            )
        )
        schemas = result.fetchall()
        # Remove 'tenant_' prefix from schema names
        return [schema[0].replace("tenant_", "") for schema in schemas]
