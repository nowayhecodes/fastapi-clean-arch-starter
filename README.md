# FastAPI Clean Arch Starter

A clean architecture boilerplate for Python FastAPI backend APIs.

## Features

- Clean Architecture implementation
- FastAPI for the web framework
- SQLAlchemy for database ORM
- PostgreSQL as the database
- Redis for caching and message broker
- Celery for background tasks
- JWT authentication
- Docker and Docker Compose for development
- Pytest for testing
- Type hints and mypy for type checking
- Ruff for linting
- UV for dependency management

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
│   │   ├── database.py
│   │   └── repository.py
│   └── presentation/
│       └── api/
│           └── v1/
│               └── api.py
├── account/
│   ├── domain/
│   ├── application/
│   └── presentation/
└── notification/
    ├── domain/
    ├── application/
    └── presentation/
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- UV (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/nowayhecodes/fastapi-clean-arch-starter.git
cd fastapi-clean-arch-starter
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install uv
uv pip install -e .
```

4. Copy the environment file:
```bash
cp .env.example .env
```

5. Start the services:
```bash
docker-compose up -d
```

6. Run database migrations:
```bash
alembic upgrade head
```

7. Start the development server:
```bash
uvicorn src.app:app --reload
```

The API will be available at http://localhost:8000

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project uses Ruff for linting and formatting. To check the code style:

```bash
ruff check .
ruff format .
```

### Type Checking

The project uses mypy for type checking:

```bash
mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 