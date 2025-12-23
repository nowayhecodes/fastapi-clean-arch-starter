# OpenTelemetry Logger Module

This module provides OpenTelemetry-compliant structured logging with automatic trace context propagation. It's designed to work seamlessly with any OpenTelemetry-compatible observability platform.

## Features

- **Structured JSON Logging**: Machine-readable logs with consistent format
- **Automatic Trace Context**: Logs include trace_id and span_id for correlation
- **OpenTelemetry Integration**: Compatible with OTLP protocol
- **Flexible Configuration**: Easy to configure for different environments
- **Multi-Platform Support**: Works with New Relic, Datadog, Jaeger, Kibana, Dynatrace, etc.

## Supported Observability Platforms

This logger works with any OpenTelemetry-compatible platform:

### New Relic
```python
configure_logging(
    service_name="my-service",
    enable_otel=True,
    otel_endpoint="https://otlp.nr-data.net:4317",
    json_logs=True
)
```

### Datadog
```python
configure_logging(
    service_name="my-service",
    enable_otel=True,
    otel_endpoint="http://localhost:4317",  # Datadog Agent
    json_logs=True
)
```

### Jaeger
```python
configure_logging(
    service_name="my-service",
    enable_otel=True,
    otel_endpoint="http://jaeger:4317",
    json_logs=True
)
```

### Elastic/Kibana
```python
configure_logging(
    service_name="my-service",
    enable_otel=True,
    otel_endpoint="http://elastic-apm:8200",
    json_logs=True
)
```

### Grafana/Tempo
```python
configure_logging(
    service_name="my-service",
    enable_otel=True,
    otel_endpoint="http://tempo:4317",
    json_logs=True
)
```

### Dynatrace
```python
configure_logging(
    service_name="my-service",
    enable_otel=True,
    otel_endpoint="https://{your-environment-id}.live.dynatrace.com/api/v2/otlp",
    json_logs=True
)
```

## Usage

### Basic Setup

```python
from src.logger import configure_logging, get_logger

# Configure logging at application startup
configure_logging(
    service_name="my-api",
    log_level="INFO",
    enable_otel=True,
    otel_endpoint="http://localhost:4317",
    json_logs=True
)

# Get a logger instance
logger = get_logger(__name__)

# Log messages
logger.info("Application started")
logger.error("An error occurred", extra={"user_id": "123"})
```

### With Additional Context

```python
# Create logger with persistent context
logger = get_logger(__name__, extra_context={"service": "api", "version": "1.0"})

# All logs from this logger will include the extra context
logger.info("Processing request")
```

### In FastAPI Application

```python
from fastapi import FastAPI
from src.logger import configure_logging
from src.logger.middleware import LoggingMiddleware

# Configure logging
configure_logging(
    service_name="fastapi-app",
    log_level="INFO",
    enable_otel=True,
    otel_endpoint=os.getenv("OTEL_ENDPOINT"),
    json_logs=True
)

app = FastAPI()

# Add logging middleware
app.add_middleware(LoggingMiddleware)
```

## Log Format

### JSON Format (Production)
```json
{
  "timestamp": "2025-12-23T10:30:45",
  "level": "INFO",
  "logger": "src.account.service",
  "message": "User created successfully",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "user_id": "123",
  "tenant_id": "acme"
}
```

### Text Format (Development)
```
2025-12-23 10:30:45 - src.account.service - INFO - User created successfully
```

## Environment Variables

Configure via environment variables:

```bash
# Service identification
OTEL_SERVICE_NAME=my-service

# OTLP endpoint
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Log level
LOG_LEVEL=INFO

# Enable JSON logs
JSON_LOGS=true
```

## Trace Context Propagation

The logger automatically includes trace context in all logs when OpenTelemetry tracing is active:

- **trace_id**: Unique identifier for the entire trace
- **span_id**: Unique identifier for the current span

This allows you to:
1. Correlate logs with traces in your observability platform
2. Search logs by trace ID
3. View logs in the context of distributed traces

## Best Practices

1. **Always use structured logging**: Pass additional data via `extra` parameter
   ```python
   logger.info("User action", extra={"user_id": "123", "action": "login"})
   ```

2. **Use appropriate log levels**:
   - `DEBUG`: Detailed diagnostic information
   - `INFO`: General informational messages
   - `WARNING`: Warning messages for potentially harmful situations
   - `ERROR`: Error messages for serious problems
   - `CRITICAL`: Critical messages for very serious errors

3. **Include context**: Add relevant context to help with debugging
   ```python
   logger.error("Database query failed", extra={
       "query": "SELECT * FROM users",
       "error_code": "23505",
       "tenant_id": tenant_id
   })
   ```

4. **Don't log sensitive data**: Never log passwords, tokens, or PII
   ```python
   # Bad
   logger.info(f"User logged in with password: {password}")
   
   # Good
   logger.info("User logged in", extra={"user_id": user_id})
   ```

## Integration with Existing Code

Replace existing logging calls:

```python
# Before
import logging
logger = logging.getLogger(__name__)
logger.info("Message")

# After
from src.logger import get_logger
logger = get_logger(__name__)
logger.info("Message")
```

## Testing

For testing, disable OTLP export:

```python
configure_logging(
    service_name="test-service",
    log_level="DEBUG",
    enable_otel=False,  # Disable for tests
    json_logs=False      # Use text format for readability
)
```

## Troubleshooting

### Logs not appearing in observability platform

1. Check OTLP endpoint is correct
2. Verify network connectivity to the endpoint
3. Check authentication/API keys if required
4. Enable debug logging: `log_level="DEBUG"`

### Missing trace context

1. Ensure OpenTelemetry is enabled: `enable_otel=True`
2. Verify middleware is added to FastAPI app
3. Check that requests are being traced

### Performance concerns

The logger uses:
- Asynchronous span export (non-blocking)
- Batch processing for traces
- Efficient JSON serialization

For high-throughput applications, consider:
- Sampling traces (not all requests need to be traced)
- Adjusting batch size in OTLP exporter
- Using appropriate log levels (avoid DEBUG in production)

