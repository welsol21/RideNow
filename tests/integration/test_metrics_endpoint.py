"""Integration coverage for the shared Prometheus metrics surface."""

from __future__ import annotations

import re

from fastapi.testclient import TestClient

from ridenow_shared import create_probe_app


def test_probe_app_exposes_prometheus_metrics_for_handled_requests() -> None:
    """Verify handled requests appear on the Prometheus metrics endpoint."""

    client = TestClient(create_probe_app("driver"))

    health_response = client.get("/health")
    metrics_response = client.get("/metrics")

    assert health_response.status_code == 200
    assert metrics_response.status_code == 200
    assert (
        metrics_response.headers["content-type"].startswith(
            "text/plain; version=0.0.4"
        )
    )
    assert re.search(
        r'ridenow_http_requests_total\{method="GET",path="/health",'
        r'service="driver",status_code="200"\} [1-9]\d*(?:\.\d+)?',
        metrics_response.text,
    )
