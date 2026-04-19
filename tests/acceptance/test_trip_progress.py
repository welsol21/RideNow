"""Acceptance test for customer-visible trip progress."""

from time import sleep

from fastapi.testclient import TestClient
import pytest

from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_trip_progress_becomes_visible_to_the_customer() -> None:
    """Verify that trip progress becomes visible after payment authorisation."""

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

    payment_response = None
    for _ in range(12):
        sleep(0.05)
        candidate = client.get(f"/rides/{ride_id}")
        if candidate.json()["status"] == "payment-authorised":
            payment_response = candidate
            break

    assert payment_response is not None
    assert payment_response.status_code == 200
    assert payment_response.json()["status"] == "payment-authorised"

    response = payment_response
    for _ in range(12):
        sleep(0.05)
        response = client.get(f"/rides/{ride_id}")
        if response.json()["status"] == "trip-in-progress":
            break

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "trip-in-progress",
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
        "progress": {
            "phase": "driver-arriving",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    }
