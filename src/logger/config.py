"""Logger configuration with OpenTelemetry support."""
import logging
import sys
from typing import Any, Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pythonjsonlogger import jsonlogger


class OpenTelemetryFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that includes OpenTelemetry trace context."""

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add OpenTelemetry trace context to log records.
        
        Args:
            log_record: The log record dictionary to populate.
            record: The original logging.LogRecord.
            message_dict: Additional message fields.
        """
        super().add_fields(log_record, record, message_dict)
        
        # Add trace context if available
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            span_context = span.get_span_context()
            log_record["trace_id"] = format(span_context.trace_id, "032x")
            log_record["span_id"] = format(span_context.span_id, "016x")
            log_record["trace_flags"] = span_context.trace_flags
        
        # Add standard fields
        log_record["logger"] = record.name
        log_record["level"] = record.levelname
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)


def configure_logging(
    service_name: str = "fastapi-app",
    log_level: str = "INFO",
    enable_otel: bool = True,
    otel_endpoint: Optional[str] = None,
    json_logs: bool = True,
) -> None:
    """Configure logging with OpenTelemetry integration.
    
    Args:
        service_name: Name of the service for tracing.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        enable_otel: Enable OpenTelemetry tracing.
        otel_endpoint: OTLP endpoint URL (e.g., "http://localhost:4317").
                      If None, traces won't be exported but context will still be available.
        json_logs: Use JSON formatted logs (recommended for production).
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Set formatter
    if json_logs:
        formatter = OpenTelemetryFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Configure OpenTelemetry
    if enable_otel:
        # Create resource with service information
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": "1.0.0",
            }
        )
        
        # Set up tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # Add OTLP exporter if endpoint is provided
        if otel_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
        
        # Instrument logging to include trace context
        LoggingInstrumentor().instrument(set_logging_format=False)


def configure_uvicorn_logging(json_logs: bool = True) -> dict[str, Any]:
    """Configure uvicorn logging to match application logging.
    
    Args:
        json_logs: Use JSON formatted logs.
        
    Returns:
        Dictionary with uvicorn logging configuration.
    """
    if json_logs:
        formatters = {
            "default": {
                "()": "src.logger.config.OpenTelemetryFormatter",
                "fmt": "%(timestamp)s %(level)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
            "access": {
                "()": "src.logger.config.OpenTelemetryFormatter",
                "fmt": "%(timestamp)s %(level)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
            },
        }
    else:
        formatters = {
            "default": {
                "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        }
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    }

