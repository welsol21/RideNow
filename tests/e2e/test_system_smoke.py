"""Live end-to-end smoke coverage for the Compose-hosted RideNow stack."""

from __future__ import annotations

import time

import httpx
import pytest


def _poll_ride_status(
    client: httpx.Client,
    ride_id: str,
    *,
    timeout_seconds: float = 8.0,
) -> dict[str, object]:
    """Poll the Broker read model until the ride reaches its final happy state."""

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        response = client.get(f"/rides/{ride_id}")
        response.raise_for_status()
        payload = response.json()
        if payload["status"] == "payment-confirmed":
            return payload
        time.sleep(0.2)
    raise AssertionError(
        "ride did not reach payment-confirmed within the smoke timeout"
    )


@pytest.mark.e2e
def test_compose_stack_supports_a_complete_customer_happy_path() -> None:
    """Verify the live Compose stack can complete the main RideNow happy path."""

    with httpx.Client(base_url="http://127.0.0.1:8001", timeout=5.0) as client:
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json() == {"service": "broker", "status": "ok"}

        request_response = client.post(
            "/rides",
            json={
                "customer_id": "customer-e2e",
                "pickup": {"lat": 53.3498, "lon": -6.2603},
                "dropoff": {"lat": 53.3440, "lon": -6.2672},
            },
        )
        assert request_response.status_code == 202

        request_payload = request_response.json()
        assert request_payload["status"] == "request-submitted"
        ride_id = str(request_payload["ride_id"])

        final_status = _poll_ride_status(client, ride_id)

        assert final_status["status"] == "payment-confirmed"
        assert final_status["driver"]["driver_id"].startswith("driver-")
        assert final_status["driver"]["vehicle_id"].startswith("vehicle-")
        assert final_status["payment"]["status"] == "captured"
