"""Logging middleware with OpenTelemetry tracing."""
import time
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from starlette.middleware.base import BaseHTTPMiddleware

from src.logger.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests with OpenTelemetry tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log with trace context.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            The response from the handler.
        """
        start_time = time.time()
        
        # Extract request information
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        
        # Get or create a span for this request
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span(
            f"{method} {path}",
            kind=trace.SpanKind.SERVER,
        ) as span:
            # Set span attributes
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.target", path)
            span.set_attribute("http.host", request.url.hostname or "unknown")
            span.set_attribute("http.scheme", request.url.scheme)
            span.set_attribute("net.peer.ip", client_host)
            
            # Add tenant ID if available
            tenant_id = request.headers.get("x-tenant-id") or request.query_params.get("tenantId")
            if tenant_id:
                span.set_attribute("tenant.id", tenant_id)
            
            try:
                # Process request
                response = await call_next(request)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Set response attributes
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.response_content_length", response.headers.get("content-length", 0))
                
                # Set span status based on response code
                if response.status_code >= 500:
                    span.set_status(Status(StatusCode.ERROR))
                else:
                    span.set_status(Status(StatusCode.OK))
                
                # Log request completion
                logger.info(
                    f"{method} {path} - {response.status_code}",
                    extra={
                        "http_method": method,
                        "http_path": path,
                        "http_status": response.status_code,
                        "duration_seconds": duration,
                        "client_ip": client_host,
                        "tenant_id": tenant_id,
                    },
                )
                
                return response
                
            except Exception as exc:
                # Calculate duration
                duration = time.time() - start_time
                
                # Record exception in span
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                
                # Log error
                logger.error(
                    f"{method} {path} - Error: {str(exc)}",
                    extra={
                        "http_method": method,
                        "http_path": path,
                        "duration_seconds": duration,
                        "client_ip": client_host,
                        "tenant_id": tenant_id,
                        "error": str(exc),
                    },
                    exc_info=True,
                )
                
                raise

