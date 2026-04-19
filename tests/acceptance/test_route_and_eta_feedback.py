"""Acceptance test for customer-visible route and ETA feedback."""

from time import sleep

from fastapi.testclient import TestClient
import pytest

from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_route_and_eta_feedback_become_visible_to_the_customer() -> None:
    """Verify that route and ETA details become visible after driver assignment."""

    client = TestClient(create_app())

    creation_response = client.post(
        "/rides",
        json={
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    first_status = client.get(f"/rides/{ride_id}")

    assert first_status.status_code == 200
    assert first_status.json()["status"] == "driver-assigned"

    response = first_status
    for _ in range(10):
        sleep(0.05)
        response = client.get(f"/rides/{ride_id}")
        if response.json()["status"] == "eta-updated":
            break

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "eta-updated",
        "driver": {
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
        "route": {
            "distance_km": 4.8,
            "pickup_eta_minutes": 3,
            "trip_duration_minutes": 11,
        },
    }
