"""Logger utilities with OpenTelemetry context."""
import logging
from typing import Any, Optional

from opentelemetry import trace


class ContextLogger(logging.LoggerAdapter):
    """Logger adapter that automatically includes trace context and custom fields."""

    def __init__(self, logger: logging.Logger, extra: Optional[dict[str, Any]] = None):
        """Initialize the context logger.
        
        Args:
            logger: The base logger instance.
            extra: Additional context fields to include in all log messages.
        """
        super().__init__(logger, extra or {})

    def process(
        self, msg: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, Any]]:
        """Process log message to add context.
        
        Args:
            msg: The log message.
            kwargs: Additional keyword arguments.
            
        Returns:
            Tuple of (message, kwargs) with added context.
        """
        # Get current span context
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            span_context = span.get_span_context()
            extra = kwargs.get("extra", {})
            extra.update(
                {
                    "trace_id": format(span_context.trace_id, "032x"),
                    "span_id": format(span_context.span_id, "016x"),
                }
            )
            kwargs["extra"] = extra

        # Add any additional context from the adapter
        if self.extra:
            extra = kwargs.get("extra", {})
            extra.update(self.extra)
            kwargs["extra"] = extra

        return msg, kwargs


def get_logger(
    name: str, extra_context: Optional[dict[str, Any]] = None
) -> ContextLogger:
    """Get a logger instance with OpenTelemetry context support.
    
    Args:
        name: Logger name (typically __name__ of the module).
        extra_context: Additional context to include in all log messages.
        
    Returns:
        ContextLogger instance with trace context support.
        
    Example:
        >>> logger = get_logger(__name__, {"service": "api"})
        >>> logger.info("User logged in", extra={"user_id": "123"})
    """
    base_logger = logging.getLogger(name)
    return ContextLogger(base_logger, extra_context)


def log_with_trace(
    logger: logging.Logger,
    level: str,
    message: str,
    **kwargs: Any,
) -> None:
    """Log a message with automatic trace context injection.
    
    Args:
        logger: The logger instance to use.
        level: Log level (debug, info, warning, error, critical).
        message: The log message.
        **kwargs: Additional fields to include in the log.
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        span_context = span.get_span_context()
        kwargs["trace_id"] = format(span_context.trace_id, "032x")
        kwargs["span_id"] = format(span_context.span_id, "016x")

    log_method = getattr(logger, level.lower())
    log_method(message, extra=kwargs)

