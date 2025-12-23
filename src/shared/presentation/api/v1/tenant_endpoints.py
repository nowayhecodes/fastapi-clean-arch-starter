"""Tenant management endpoints for creating and managing tenant schemas."""
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.shared.infra.database import (
    create_tenant_schema,
    drop_tenant_schema,
    list_tenant_schemas,
)

router = APIRouter()


class TenantCreate(BaseModel):
    """Schema for creating a new tenant."""
    
    tenant_id: str = Field(
        ...,
        description="Unique tenant identifier (alphanumeric and underscores only)",
        pattern="^[a-zA-Z0-9_]+$",
        min_length=1,
        max_length=50,
    )


class TenantResponse(BaseModel):
    """Response schema for tenant operations."""
    
    tenant_id: str
    message: str


class TenantListResponse(BaseModel):
    """Response schema for listing tenants."""
    
    tenants: list[str]
    count: int


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(tenant_data: TenantCreate) -> Any:
    """Create a new tenant schema in the database.
    
    This endpoint creates a new PostgreSQL schema for the tenant and initializes
    all required tables within that schema.
    
    Args:
        tenant_data: Tenant creation data containing the tenant ID.
        
    Returns:
        TenantResponse with the created tenant ID and success message.
        
    Raises:
        HTTPException: If tenant creation fails.
    """
    try:
        await create_tenant_schema(tenant_data.tenant_id)
        return TenantResponse(
            tenant_id=tenant_data.tenant_id,
            message=f"Tenant '{tenant_data.tenant_id}' created successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tenant: {str(e)}",
        ) from e


@router.delete("/{tenant_id}", response_model=TenantResponse)
async def delete_tenant(tenant_id: str) -> Any:
    """Delete a tenant schema and all its data.
    
    WARNING: This permanently deletes all data for the tenant.
    
    Args:
        tenant_id: The tenant identifier to delete.
        
    Returns:
        TenantResponse with the deleted tenant ID and success message.
        
    Raises:
        HTTPException: If tenant deletion fails.
    """
    try:
        await drop_tenant_schema(tenant_id, cascade=True)
        return TenantResponse(
            tenant_id=tenant_id,
            message=f"Tenant '{tenant_id}' deleted successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tenant: {str(e)}",
        ) from e


@router.get("/", response_model=TenantListResponse)
async def list_tenants() -> Any:
    """List all tenant schemas in the database.
    
    Returns:
        TenantListResponse with list of tenant IDs and count.
        
    Raises:
        HTTPException: If listing tenants fails.
    """
    try:
        tenants = await list_tenant_schemas()
        return TenantListResponse(
            tenants=tenants,
            count=len(tenants),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tenants: {str(e)}",
        ) from e

