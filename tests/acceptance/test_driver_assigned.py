"""Acceptance test for customer-visible driver assignment."""

from fastapi.testclient import TestClient
import pytest

from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_driver_assignment_becomes_visible_to_the_customer() -> None:
    """Verify that the customer can observe a driver-assigned ride state."""

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
    response = client.get(f"/rides/{ride_id}")

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "driver-assigned",
        "driver": {
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
    }
