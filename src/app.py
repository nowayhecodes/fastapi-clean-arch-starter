import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.compliance.security import SecurityHeadersMiddleware
from src.logger import configure_logging
from src.logger.middleware import LoggingMiddleware
from src.shared.infra.config import settings
from src.shared.infra.database import init_db
from src.shared.infra.tenant_middleware import TenantMiddleware
from src.shared.presentation.api.v1.api import api_router

# Configure logging at module level
configure_logging(
    service_name=settings.PROJECT_NAME,
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    enable_otel=os.getenv("ENABLE_OTEL", "true").lower() == "true",
    otel_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
    json_logs=os.getenv("JSON_LOGS", "true").lower() == "true",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    await init_db()
    yield
    # Shutdown: Add any cleanup code here if needed


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # Set up CORS middleware (must be added before other middleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add security headers middleware (OWASP compliance)
    application.add_middleware(SecurityHeadersMiddleware)

    # Add logging middleware with OpenTelemetry tracing
    application.add_middleware(LoggingMiddleware)

    # Add tenant middleware for multi-schema support
    application.add_middleware(TenantMiddleware)

    # Include API router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()
