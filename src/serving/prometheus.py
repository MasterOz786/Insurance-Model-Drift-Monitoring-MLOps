"""
Prometheus Metrics Exporter for FastAPI
Exposes metrics for API inference latency, request count, and data drift
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from fastapi import Response
import time

# API Metrics
api_request_count = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status"],
)

api_request_latency = Histogram(
    "api_request_duration_seconds",
    "API request latency in seconds",
    ["method", "endpoint"],
)

# Model Metrics
model_predictions_total = Counter(
    "model_predictions_total",
    "Total number of model predictions",
    ["model_version", "status"],
)

model_prediction_latency = Histogram(
    "model_prediction_duration_seconds",
    "Model prediction latency in seconds",
    ["model_version"],
)

# Data Drift Metrics
data_drift_ratio = Gauge(
    "data_drift_ratio",
    "Ratio of requests with out-of-distribution features",
    ["feature_name"],
)

out_of_distribution_count = Counter(
    "out_of_distribution_requests_total",
    "Total number of requests with out-of-distribution features",
    ["feature_name"],
)


def get_metrics():
    """Return Prometheus metrics in text format"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def track_request(method: str, endpoint: str, status_code: int, duration: float):
    """Track API request metrics"""
    api_request_count.labels(method=method, endpoint=endpoint, status=status_code).inc()
    api_request_latency.labels(method=method, endpoint=endpoint).observe(duration)


def track_prediction(model_version: str, duration: float, status: str = "success"):
    """Track model prediction metrics"""
    model_predictions_total.labels(model_version=model_version, status=status).inc()
    model_prediction_latency.labels(model_version=model_version).observe(duration)


def track_data_drift(feature_name: str, is_drift: bool):
    """Track data drift metrics"""
    if is_drift:
        out_of_distribution_count.labels(feature_name=feature_name).inc()

    # Update drift ratio (this would be calculated from recent requests)
    # For simplicity, we'll use a counter-based approach
    # In production, you'd calculate this from a sliding window


class PrometheusMiddleware:
    """Middleware to track requests automatically"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                track_request(method, path, status_code, duration)
            await send(message)

        await self.app(scope, receive, send_wrapper)
