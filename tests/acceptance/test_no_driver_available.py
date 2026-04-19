"""Acceptance test for customer-visible no-driver-available outcome."""

from time import sleep

from fastapi.testclient import TestClient
import pytest

from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_no_driver_available_becomes_visible_to_the_customer() -> None:
    """Verify that a missing-driver outcome becomes visible to the customer."""

    client = TestClient(create_app())

    creation_response = client.post(
        "/rides",
        json={
            "customer_id": "customer-no-driver",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )

    ride_id = creation_response.json()["ride_id"]
    response = None
    for _ in range(12):
        sleep(0.05)
        response = client.get(f"/rides/{ride_id}")
        if response.json()["status"] == "no-driver-available":
            break

    assert response is not None
    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "no-driver-available",
    }
