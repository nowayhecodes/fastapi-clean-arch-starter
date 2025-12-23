# FastAPI Clean Arch Starter

A clean architecture boilerplate for Python FastAPI backend APIs with enterprise-grade features.

## 🚀 Features

### Core Architecture
- **Clean Architecture** implementation with proper layer separation
- **Dependency Injection** & Inversion of Control (IoC) following SOLID principles
- **FastAPI** for the web framework with built-in DI system
- **SQLAlchemy** for database ORM
- **PostgreSQL** as the database
- **Redis** for caching and message broker
- **Celery** for background tasks
- **JWT** authentication
- **Docker** and Docker Compose for development
- **Pytest** for testing with dependency mocking
- **Type hints** and mypy for type checking
- **Ruff** for linting
- **UV** for dependency management

### 🏢 Multi-Tenant Support
- **Schema-per-tenant isolation**: Complete data separation using PostgreSQL schemas
- **Automatic tenant context**: Request-scoped database sessions with tenant identification
- **Flexible tenant identification**: Support for both header (`x-tenant-id`) and query parameter (`tenantId`)
- **Tenant management API**: Complete CRUD operations for tenant schemas
- **Zero configuration**: Automatic schema switching and management

### 📊 OpenTelemetry Observability
- **Structured JSON logging**: Machine-readable logs with consistent format
- **Distributed tracing**: Automatic trace context propagation across services
- **Multi-platform support**: Works with any OpenTelemetry-compatible platform:
  - New Relic
  - Datadog
  - Jaeger
  - Elastic/Kibana
  - Grafana/Tempo
  - Dynatrace
  - And more...
- **Automatic correlation**: Logs include trace_id and span_id for easy correlation
- **Performance monitoring**: Built-in request/response tracking

### 🔒 Compliance & Security (LGPD/GDPR/OWASP)
- **Data Privacy (LGPD/GDPR)**:
  - Consent management system
  - Data subject rights (access, rectification, erasure, portability)
  - Data anonymization utilities
  - Audit logging for compliance
  - Data retention policies
  
- **Security (OWASP Top 10)**:
  - Security headers (XSS, clickjacking, CSP, HSTS)
  - Rate limiting (IP-based)
  - Password policy enforcement
  - Input sanitization
  - CSRF protection
  
- **Audit & Encryption**:
  - Comprehensive audit logging
  - AES-256 encryption at rest
  - Key management and rotation
  - Security event monitoring

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup and configuration guide
- **[DEPENDENCY_INJECTION.md](DEPENDENCY_INJECTION.md)** - Dependency injection & IoC patterns
- **[src/logger/README.md](src/logger/README.md)** - Logger module documentation
- **[src/compliance/README.md](src/compliance/README.md)** - Compliance features documentation

## Dependencies

This section explains why each dependency is included in the project:

### Core Framework
- **fastapi**: Modern, fast web framework for building APIs with automatic OpenAPI documentation, type validation, and async support
- **uvicorn**: ASGI server used for running FastAPI applications in development, providing high performance with async support
- **gunicorn**: Production-ready WSGI/ASGI HTTP server that manages worker processes, used with uvicorn workers for production deployments
- **uvloop**: High-performance event loop implementation that replaces the default asyncio event loop, significantly improving async I/O performance
- **httptools**: Fast HTTP parsing library that enhances uvicorn's performance by providing optimized HTTP protocol parsing

### Database & ORM
- **sqlalchemy**: Powerful ORM that provides database abstraction, connection pooling, and query building for PostgreSQL
- **asyncpg**: High-performance async PostgreSQL driver that enables non-blocking database operations, essential for async FastAPI applications
- **alembic**: Database migration tool that manages schema changes, versioning, and rollbacks for SQLAlchemy models

### Data Validation & Serialization
- **pydantic**: Data validation library used by FastAPI for request/response validation, type coercion, and settings management
- **email-validator**: Validates email addresses according to RFC standards, used with Pydantic for email field validation

### Authentication & Security
- **python-jose[cryptography]**: JWT token encoding and decoding library for implementing stateless authentication
- **passlib[bcrypt]**: Password hashing library that provides secure password storage using bcrypt algorithm

### File Handling
- **python-multipart**: Required for handling file uploads and form data in FastAPI endpoints

### Caching & Message Broker
- **redis**: In-memory data store used for caching frequently accessed data and as a message broker for Celery tasks

### Background Tasks
- **celery**: Distributed task queue system for executing long-running or scheduled tasks asynchronously, integrated with Redis as the broker

### Testing
- **pytest**: Comprehensive testing framework with fixtures, parametrization, and extensive plugin ecosystem
- **pytest-asyncio**: Plugin that enables testing of async functions and coroutines with pytest
- **httpx**: Async HTTP client library used for making test requests to FastAPI endpoints and for external API calls in the application

### Configuration & Environment
- **python-dotenv**: Loads environment variables from `.env` files, making configuration management easier across different environments

### Observability & Logging
- **prometheus-client**: Exposes application metrics in Prometheus format for monitoring and alerting
- **python-json-logger**: Provides structured JSON logging output, making logs easier to parse and analyze
- **structlog**: Advanced structured logging library that provides context-aware logging with better performance and flexibility
- **opentelemetry-api**: Core OpenTelemetry API for instrumentation
- **opentelemetry-sdk**: OpenTelemetry SDK for trace and metric collection
- **opentelemetry-exporter-otlp-proto-grpc**: OTLP exporter for sending telemetry data to observability platforms
- **opentelemetry-instrumentation-fastapi**: Automatic FastAPI instrumentation for tracing
- **opentelemetry-instrumentation-logging**: Automatic logging instrumentation with trace context
- **opentelemetry-instrumentation-sqlalchemy**: Automatic SQLAlchemy query tracing
- **opentelemetry-instrumentation-redis**: Automatic Redis operation tracing

### Security & Compliance
- **slowapi**: Rate limiting library for FastAPI applications
- **cryptography**: Cryptographic recipes and primitives for data encryption at rest
- **pydantic-settings**: Settings management with environment variable support

## Project Structure

```
src/
├── shared/
│   ├── domain/
│   │   ├── base.py
│   │   └── repository.py
│   ├── application/
│   │   ├── service.py
│   │   └── crud_service.py
│   ├── infra/
│   │   ├── config.py
│   │   ├── database.py              # Multi-schema support
│   │   ├── tenant_context.py        # Tenant context management
│   │   ├── tenant_middleware.py     # Tenant middleware
│   │   └── repository.py
│   └── presentation/
│       └── api/
│           └── v1/
│               ├── api.py
│               └── tenant_endpoints.py  # Tenant management API
├── logger/                          # OpenTelemetry logger module
│   ├── __init__.py
│   ├── config.py                    # Logger configuration
│   ├── logger.py                    # Logger utilities
│   ├── middleware.py                # Logging middleware
│   └── README.md
├── compliance/                      # LGPD/GDPR/OWASP compliance
│   ├── __init__.py
│   ├── data_privacy.py              # Privacy features
│   ├── security.py                  # Security features
│   ├── audit_log.py                 # Audit logging
│   ├── data_retention.py            # Retention & encryption
│   ├── endpoints.py                 # Compliance API
│   └── README.md
├── account/
│   ├── domain/
│   ├── application/
│   └── presentation/
└── notification/
    ├── domain/
    ├── application/
    └── presentation/
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker and Docker Compose (optional)
- UV (Python package manager)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/nowayhecodes/fastapi-clean-arch-starter.git
cd fastapi-clean-arch-starter
```

2. **Install dependencies:**
```bash
uv sync
# or
pip install -e .
```

3. **Configure environment:**
```bash
# Create .env file with required variables
# See SETUP_GUIDE.md for all options

# Generate secure keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('MASTER_ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
```

4. **Start services:**
```bash
docker-compose up -d
```

5. **Run database migrations:**
```bash
# Create migration for new features
python scripts/create_migration.py

# Apply migrations
alembic upgrade head
```

6. **Create your first tenant:**
```bash
# Start the application
uvicorn src.app:app --reload

# Create tenant
curl -X POST http://localhost:8000/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "demo"}'
```

7. **Access the API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Making Requests

All API requests require tenant identification:

```bash
# Using header (recommended)
curl -H "x-tenant-id: demo" http://localhost:8000/api/v1/account/me

# Using query parameter
curl "http://localhost:8000/api/v1/account/me?tenantId=demo"
```

For detailed setup instructions, see **[SETUP_GUIDE.md](SETUP_GUIDE.md)**

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_app.py
```

### Code Style

```bash
# Check code style
ruff check .

# Format code
ruff format .
```

### Type Checking

```bash
mypy .
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see SETUP_GUIDE.md for complete list):

```bash
# Database
POSTGRES_SERVER=localhost
POSTGRES_DB=fastapi_db

# Security
SECRET_KEY=your-secret-key
MASTER_ENCRYPTION_KEY=your-encryption-key

# OpenTelemetry
OTEL_SERVICE_NAME=fastapi-app
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
ENABLE_OTEL=true
JSON_LOGS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## 📖 API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Key Endpoints

#### Tenant Management
```
POST   /api/v1/tenants              # Create tenant
GET    /api/v1/tenants              # List tenants
DELETE /api/v1/tenants/{tenant_id}  # Delete tenant
```

#### Compliance
```
POST   /api/v1/compliance/consent                    # Record consent
GET    /api/v1/compliance/consent/{user}/{type}      # Check consent
DELETE /api/v1/compliance/consent/{user}/{type}      # Revoke consent
POST   /api/v1/compliance/data-subject-request       # Create request
GET    /api/v1/compliance/data-export/{user_id}      # Export data
DELETE /api/v1/compliance/user-data/{user_id}        # Delete data
```

## 🔒 Security

This project implements:
- OWASP Top 10 security best practices
- LGPD and GDPR compliance features
- Rate limiting and DDoS protection
- Security headers on all responses
- Password policy enforcement
- Data encryption at rest
- Comprehensive audit logging

See **[src/compliance/README.md](src/compliance/README.md)** for details.

## 🌍 Multi-Platform Observability

The logger module works with any OpenTelemetry-compatible platform:

- **New Relic**: Enterprise APM and observability
- **Datadog**: Full-stack monitoring
- **Jaeger**: Open-source distributed tracing
- **Elastic/Kibana**: Log aggregation and analysis
- **Grafana/Tempo**: Metrics and tracing
- **Dynatrace**: Application performance monitoring

See **[src/logger/README.md](src/logger/README.md)** for configuration examples.

## 📊 Monitoring

### Logs
- Structured JSON logs with trace context
- Automatic correlation with distributed traces
- Compatible with any log aggregation platform

### Traces
- Distributed tracing with OpenTelemetry
- Automatic span creation for HTTP requests
- Custom spans for business logic

### Audit Logs
- All sensitive operations logged
- Compliance audit trail
- Security event monitoring

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenTelemetry](https://opentelemetry.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/) 