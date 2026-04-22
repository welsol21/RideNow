"""Monitoring-stack validation for the Compose-hosted demo environment."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import pytest
from tests.nonfunctional.runtime_helpers import broker_client, prometheus_query


@pytest.mark.nonfunctional
def test_prometheus_reports_all_service_targets_as_up() -> None:
    """Verify Prometheus sees every RideNow service target as healthy."""

    with broker_client() as client:
        metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    assert "ridenow_http_requests_total" in metrics_response.text

    query_result = prometheus_query("up")
    data = query_result["data"]
    if not isinstance(data, Mapping):
        raise AssertionError("unexpected Prometheus query data payload")
    result = data["result"]
    if not isinstance(result, Iterable):
        raise AssertionError("unexpected Prometheus query result payload")
    targets = {
        str(entry["metric"]["job"]): str(entry["value"][1])
        for entry in result
        if isinstance(entry, Mapping)
        and isinstance(entry.get("metric"), Mapping)
        and isinstance(entry.get("value"), list)
    }

    assert targets == {
        "broker": "1",
        "driver": "1",
        "notification": "1",
        "payment": "1",
        "pricing": "1",
        "route": "1",
        "tracking": "1",
    }
