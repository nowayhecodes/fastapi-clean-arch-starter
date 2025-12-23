"""Middleware for extracting and setting tenant context from requests."""
from collections.abc import Callable
from typing import ClassVar

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.shared.infra.tenant_context import TenantContext


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract tenant ID from request and set it in context.
    
    The tenant ID can be provided via:
    1. Header: x-tenant-id
    2. Query parameter: tenantId
    
    If no tenant ID is provided, returns a 400 Bad Request error.
    """

    TENANT_HEADER: ClassVar[str] = "x-tenant-id"
    TENANT_QUERY_PARAM: ClassVar[str] = "tenantId"
    
    # Paths that don't require tenant ID (e.g., health checks, docs)
    EXCLUDED_PATHS: ClassVar[list[str]] = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/metrics",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and extract tenant ID.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            The response from the next handler or an error response.
        """
        # Skip tenant validation for excluded paths
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return await call_next(request)

        # Extract tenant ID from header or query parameter
        tenant_id = request.headers.get(self.TENANT_HEADER)
        
        if not tenant_id:
            tenant_id = request.query_params.get(self.TENANT_QUERY_PARAM)

        if not tenant_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": (
                        f"Tenant ID is required. Provide it via "
                        f"'{self.TENANT_HEADER}' header or "
                        f"'{self.TENANT_QUERY_PARAM}' query parameter."
                    )
                },
            )

        # Validate tenant ID format (alphanumeric and underscores only)
        if not tenant_id.replace("_", "").isalnum():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": (
                        "Invalid tenant ID format. Only alphanumeric "
                        "characters and underscores are allowed."
                    )
                },
            )

        # Set tenant ID in context
        TenantContext.set_tenant_id(tenant_id)

        try:
            response = await call_next(request)
            return response
        finally:
            # Clear tenant context after request
            TenantContext.clear_tenant_id()

