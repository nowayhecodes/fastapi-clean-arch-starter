# Setup Guide

This guide will help you set up and configure the FastAPI Clean Architecture Starter with all the new features.

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for Celery)
- Docker (optional, for containerized deployment)

## Installation

### 1. Clone and Install Dependencies

```bash
# Install dependencies using uv (recommended) or pip
uv sync

# Or with pip
pip install -e .
```

### 2. Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Application Settings
APP_NAME=fastapi-clean-arch-starter
APP_ENV=development
DEBUG=true
API_V1_STR=/api/v1
PROJECT_NAME=FastAPI Clean Architecture Starter

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_db
SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@localhost/fastapi_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=noreply@example.com
EMAILS_FROM_NAME=FastAPI App

# OpenTelemetry / Logging
OTEL_SERVICE_NAME=fastapi-app
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
LOG_LEVEL=INFO
JSON_LOGS=true
ENABLE_OTEL=true

# Compliance / Security
MASTER_ENCRYPTION_KEY=your-master-encryption-key-change-in-production
RATE_LIMIT_PER_MINUTE=60
PASSWORD_MIN_LENGTH=12
```

### 3. Database Setup

```bash
# Create database
createdb fastapi_db

# Run migrations
alembic revision --autogenerate -m "Initial migration with multi-tenant and compliance tables"
alembic upgrade head
```

### 4. Generate Secure Keys

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate MASTER_ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Feature Configuration

### Multi-Tenant Setup

#### 1. Create Tenants

```bash
# Start the application
uvicorn src.app:app --reload

# Create a tenant
curl -X POST http://localhost:8000/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "acme"}'

# List all tenants
curl -X GET http://localhost:8000/api/v1/tenants
```

#### 2. Use Tenant Context

All API requests must include tenant identification:

**Option 1: Header (Recommended)**
```bash
curl -X GET http://localhost:8000/api/v1/account/me \
  -H "x-tenant-id: acme"
```

**Option 2: Query Parameter**
```bash
curl -X GET "http://localhost:8000/api/v1/account/me?tenantId=acme"
```

### OpenTelemetry Setup

#### Option 1: Jaeger (Development)

```bash
# Start Jaeger
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest

# Configure in .env
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
ENABLE_OTEL=true

# View traces at http://localhost:16686
```

#### Option 2: New Relic

```bash
# Configure in .env
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317
OTEL_EXPORTER_OTLP_HEADERS=api-key=YOUR_NEW_RELIC_LICENSE_KEY
ENABLE_OTEL=true
```

#### Option 3: Datadog

```bash
# Start Datadog Agent
docker run -d --name datadog-agent \
  -e DD_API_KEY=YOUR_DATADOG_API_KEY \
  -e DD_OTLP_CONFIG_RECEIVER_PROTOCOLS_GRPC_ENDPOINT=0.0.0.0:4317 \
  -p 4317:4317 \
  datadog/agent:latest

# Configure in .env
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
ENABLE_OTEL=true
```

#### Option 4: Elastic APM

```bash
# Configure in .env
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-elastic-apm:8200
ENABLE_OTEL=true
```

#### Disable OpenTelemetry (Testing)

```bash
# In .env
ENABLE_OTEL=false
JSON_LOGS=false
LOG_LEVEL=DEBUG
```

### Compliance Setup

#### 1. Initialize Compliance Tables

The compliance tables are automatically created when you run migrations:
- `user_consents`
- `data_processing_logs`
- `data_subject_requests`
- `audit_logs`
- `data_retention_records`
- `encryption_keys`

#### 2. Configure Encryption

```bash
# Generate master encryption key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
MASTER_ENCRYPTION_KEY=your-generated-key
```

#### 3. Test Compliance Features

```bash
# Record consent
curl -X POST http://localhost:8000/api/v1/compliance/consent \
  -H "x-tenant-id: acme" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "consent_type": "marketing",
    "granted": true,
    "consent_text": "I agree to receive marketing emails"
  }'

# Check consent
curl -X GET http://localhost:8000/api/v1/compliance/consent/user123/marketing \
  -H "x-tenant-id: acme"

# Export user data (GDPR/LGPD)
curl -X GET http://localhost:8000/api/v1/compliance/data-export/user123 \
  -H "x-tenant-id: acme"

# Request data deletion
curl -X DELETE http://localhost:8000/api/v1/compliance/user-data/user123 \
  -H "x-tenant-id: acme"
```

## Running the Application

### Development

```bash
# With uvicorn
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# With the start script
chmod +x start.sh
./start.sh
```

### Production

```bash
# With gunicorn
gunicorn src.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

### Docker

```bash
# Build image
docker build -t fastapi-app .

# Run container
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  --env-file .env \
  fastapi-app
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_app.py
```

### Test Multi-Tenant Isolation

```bash
# Create two tenants
curl -X POST http://localhost:8000/api/v1/tenants -d '{"tenant_id": "tenant1"}'
curl -X POST http://localhost:8000/api/v1/tenants -d '{"tenant_id": "tenant2"}'

# Create data in tenant1
curl -X POST http://localhost:8000/api/v1/account \
  -H "x-tenant-id: tenant1" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@tenant1.com", "password": "SecurePass123!", "full_name": "User One"}'

# Try to access from tenant2 (should not see tenant1 data)
curl -X GET http://localhost:8000/api/v1/account \
  -H "x-tenant-id: tenant2"
```

### Test OpenTelemetry Integration

```bash
# Make some requests
for i in {1..10}; do
  curl -X GET http://localhost:8000/api/v1/account/me \
    -H "x-tenant-id: acme"
done

# View traces in Jaeger: http://localhost:16686
# Search for service: fastapi-app
```

### Test Security Headers

```bash
# Check security headers
curl -I http://localhost:8000/api/v1/account/me \
  -H "x-tenant-id: acme"

# Should include:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Content-Security-Policy: ...
# Strict-Transport-Security: ...
```

### Test Rate Limiting

```bash
# Rapid requests to trigger rate limit
for i in {1..70}; do
  curl -X GET http://localhost:8000/api/v1/account/me \
    -H "x-tenant-id: acme"
done

# Should receive 429 Too Many Requests after 60 requests
```

## Monitoring

### Application Logs

```bash
# View logs
tail -f logs/app.log

# With JSON logs enabled, you can use jq for filtering
tail -f logs/app.log | jq 'select(.level == "ERROR")'

# Filter by trace_id
tail -f logs/app.log | jq 'select(.trace_id == "your-trace-id")'
```

### Metrics

The application exposes Prometheus metrics (if configured):

```bash
# View metrics
curl http://localhost:8001/metrics
```

### Health Check

```bash
# Basic health check
curl http://localhost:8000/health
```

## Maintenance

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Data Retention Cleanup

Create a scheduled job to clean up expired data:

```python
# cleanup_job.py
import asyncio
from src.shared.infra.database import AsyncSessionLocal
from src.compliance.data_retention import DataRetentionManager

async def cleanup_expired_data():
    async with AsyncSessionLocal() as db:
        expired = await DataRetentionManager.get_expired_data(db)
        for record in expired:
            # Delete actual data based on resource_type and resource_id
            # Then mark as deleted
            await DataRetentionManager.mark_as_deleted(db, record)

if __name__ == "__main__":
    asyncio.run(cleanup_expired_data())
```

Schedule with cron:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/venv/bin/python /path/to/cleanup_job.py
```

### Key Rotation

```python
# rotate_keys.py
import asyncio
from src.shared.infra.database import AsyncSessionLocal
from src.compliance.data_retention import EncryptionManager
import os

async def rotate_encryption_keys():
    async with AsyncSessionLocal() as db:
        master_key = os.getenv("MASTER_ENCRYPTION_KEY")
        await EncryptionManager.rotate_key(db, "main", master_key)

if __name__ == "__main__":
    asyncio.run(rotate_encryption_keys())
```

### Backup

```bash
# Backup all tenant schemas
pg_dump -h localhost -U postgres fastapi_db > backup.sql

# Backup specific tenant
pg_dump -h localhost -U postgres -n tenant_acme fastapi_db > tenant_acme_backup.sql

# Restore
psql -h localhost -U postgres fastapi_db < backup.sql
```

## Troubleshooting

### Tenant Not Found Error

```
Error: Tenant ID not found in context
```

**Solution**: Ensure you're including the tenant ID in your requests:
```bash
curl -H "x-tenant-id: your-tenant-id" ...
```

### OpenTelemetry Connection Error

```
Error: Failed to export traces to OTLP endpoint
```

**Solution**: 
1. Check if the OTLP endpoint is reachable
2. Verify the endpoint URL in .env
3. For testing, disable OTEL: `ENABLE_OTEL=false`

### Database Schema Not Found

```
Error: schema "tenant_xxx" does not exist
```

**Solution**: Create the tenant schema:
```bash
curl -X POST http://localhost:8000/api/v1/tenants \
  -d '{"tenant_id": "xxx"}'
```

### Rate Limit Exceeded

```
Error: 429 Too Many Requests
```

**Solution**: 
1. Wait for the rate limit window to reset (60 seconds)
2. Adjust rate limit in .env: `RATE_LIMIT_PER_MINUTE=120`

## Production Checklist

- [ ] Change SECRET_KEY and MASTER_ENCRYPTION_KEY
- [ ] Set DEBUG=false
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure production database with connection pooling
- [ ] Set up log aggregation (ELK, Splunk, etc.)
- [ ] Configure OpenTelemetry for your monitoring platform
- [ ] Set up automated backups
- [ ] Configure rate limiting based on your needs
- [ ] Set up health checks and monitoring
- [ ] Configure firewall rules
- [ ] Set up automated data retention cleanup
- [ ] Schedule key rotation
- [ ] Configure email service
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Review and test security headers
- [ ] Conduct security audit
- [ ] Set up CI/CD pipeline
- [ ] Document API endpoints
- [ ] Train team on compliance features

## Support

For issues or questions:
1. Check the documentation in each module's README
2. Review the IMPLEMENTATION_SUMMARY.md
3. Check logs for error details
4. Review the compliance checklist for LGPD/GDPR/OWASP requirements

## Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- OpenTelemetry Python: https://opentelemetry.io/docs/instrumentation/python/
- LGPD: https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd
- GDPR: https://gdpr.eu/
- OWASP: https://owasp.org/

