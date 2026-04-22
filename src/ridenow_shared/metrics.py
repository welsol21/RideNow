"""Prometheus metrics helpers shared across RideNow services."""

from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response as PlainResponse

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import FastAPI, Request, Response

REQUEST_COUNTER = Counter(
    "ridenow_http_requests_total",
    "Total HTTP requests handled by RideNow services.",
    ["service", "method", "path", "status_code"],
)
REQUEST_DURATION = Histogram(
    "ridenow_http_request_duration_seconds",
    "HTTP request duration for RideNow services.",
    ["service", "method", "path"],
)


def attach_metrics(app: FastAPI, service_name: str) -> None:
    """Attach Prometheus metrics middleware and `/metrics` to a FastAPI app."""

    @app.get("/metrics")
    def metrics() -> PlainResponse:
        """Expose process metrics in Prometheus text format."""

        return PlainResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.middleware("http")
    async def measure_request(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path = request.url.path
        method = request.method
        started_at = perf_counter()
        response = await call_next(request)
        REQUEST_COUNTER.labels(
            service=service_name,
            method=method,
            path=path,
            status_code=str(response.status_code),
        ).inc()
        REQUEST_DURATION.labels(
            service=service_name,
            method=method,
            path=path,
        ).observe(perf_counter() - started_at)
        return response
