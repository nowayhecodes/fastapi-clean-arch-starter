"""Tenant context management for multi-schema database support."""
from contextvars import ContextVar
from typing import Optional

# Context variable to store the current tenant ID for the request
_tenant_id_context: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)


class TenantContext:
    """Manages tenant context for the current request."""

    @staticmethod
    def get_tenant_id() -> Optional[str]:
        """Get the current tenant ID from context.
        
        Returns:
            The tenant ID if set, None otherwise.
        """
        return _tenant_id_context.get()

    @staticmethod
    def set_tenant_id(tenant_id: str) -> None:
        """Set the tenant ID in the current context.
        
        Args:
            tenant_id: The tenant identifier to set.
        """
        _tenant_id_context.set(tenant_id)

    @staticmethod
    def clear_tenant_id() -> None:
        """Clear the tenant ID from the current context."""
        _tenant_id_context.set(None)


def get_current_tenant_id() -> Optional[str]:
    """Convenience function to get the current tenant ID.
    
    Returns:
        The current tenant ID or None.
    """
    return TenantContext.get_tenant_id()

