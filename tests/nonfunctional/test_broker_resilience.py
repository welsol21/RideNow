"""Resilience validation for Compose-hosted RideNow services."""

from __future__ import annotations

import pytest
from tests.nonfunctional.runtime_helpers import (
    broker_client,
    restart_compose_service,
    ride_request_payload,
    wait_for_broker_readiness,
)


@pytest.mark.nonfunctional
def test_broker_recovers_after_container_restart() -> None:
    """Verify Broker returns to ready state and accepts new work after restart."""

    wait_for_broker_readiness()

    restart_compose_service("broker")
    wait_for_broker_readiness()

    with broker_client() as client:
        response = client.post("/rides", json=ride_request_payload(200))

    assert response.status_code == 202
    assert response.json()["status"] == "request-submitted"
