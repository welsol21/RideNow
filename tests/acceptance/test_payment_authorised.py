"""Acceptance test for customer-visible payment authorisation."""

from time import sleep

from fastapi.testclient import TestClient
import pytest

from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_payment_authorisation_becomes_visible_to_the_customer() -> None:
    """Verify that payment authorisation becomes visible after route feedback."""

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

    eta_response = None
    for _ in range(10):
        sleep(0.05)
        candidate = client.get(f"/rides/{ride_id}")
        if candidate.json()["status"] == "eta-updated":
            eta_response = candidate
            break

    assert eta_response is not None
    assert eta_response.status_code == 200
    assert eta_response.json()["status"] == "eta-updated"

    response = eta_response
    for _ in range(10):
        sleep(0.05)
        response = client.get(f"/rides/{ride_id}")
        if response.json()["status"] == "payment-authorised":
            break

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "payment-authorised",
        "driver": {
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
        "route": {
            "distance_km": 4.8,
            "pickup_eta_minutes": 3,
            "trip_duration_minutes": 11,
        },
        "payment": {
            "authorisation_id": "auth-ride-1",
            "amount": 18.5,
            "currency": "EUR",
        },
    }
