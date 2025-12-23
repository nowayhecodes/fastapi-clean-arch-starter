"""OpenTelemetry-compliant logging module.

This module provides structured logging with OpenTelemetry integration,
allowing seamless integration with various observability platforms like:
- New Relic
- Datadog
- Jaeger
- Kibana/Elastic
- Dynatrace
- Grafana/Loki
- And any other OpenTelemetry-compatible platform
"""
from src.logger.config import configure_logging
from src.logger.logger import get_logger

__all__ = ["configure_logging", "get_logger"]

