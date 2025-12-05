import time
from collections.abc import Callable

import prometheus_client
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, start_http_server
from starlette.middleware.base import BaseHTTPMiddleware

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        method = request.method
        endpoint = request.url.path

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

        return response


def start_metrics_server(port: int = 8001):
    start_http_server(port)
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
