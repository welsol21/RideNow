"""Live service-probe smoke coverage for the Compose-hosted RideNow stack."""

from __future__ import annotations

import httpx
import pytest

SERVICE_PORTS = {
    "broker": 8001,
    "driver": 8002,
    "route": 8003,
    "pricing": 8004,
    "payment": 8005,
    "tracking": 8006,
    "notification": 8007,
}


@pytest.mark.e2e
@pytest.mark.parametrize(("service_name", "port"), SERVICE_PORTS.items())
def test_compose_services_expose_health_and_readiness(
    service_name: str,
    port: int,
) -> None:
    """Verify every Compose service exposes healthy and ready probes."""

    with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5.0) as client:
        health_response = client.get("/health")
        ready_response = client.get("/ready")

    assert health_response.status_code == 200
    assert health_response.json() == {
        "service": service_name,
        "status": "ok",
    }
    assert ready_response.status_code == 200
    assert ready_response.json() == {
        "service": service_name,
        "status": "ready",
    }
