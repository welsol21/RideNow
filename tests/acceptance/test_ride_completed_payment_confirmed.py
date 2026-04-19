"""Acceptance test for ride completion and payment confirmation."""

from time import sleep

from fastapi.testclient import TestClient
import pytest

from ridenow_broker.bootstrap.app import create_app


@pytest.mark.acceptance
def test_ride_completion_and_payment_confirmation_become_visible() -> None:
    """Verify that ride completion and payment confirmation become customer-visible."""

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

    progress_response = None
    for _ in range(14):
        sleep(0.05)
        candidate = client.get(f"/rides/{ride_id}")
        if candidate.json()["status"] == "trip-in-progress":
            progress_response = candidate
            break

    assert progress_response is not None
    assert progress_response.status_code == 200
    assert progress_response.json()["status"] == "trip-in-progress"

    completed_response = progress_response
    for _ in range(14):
        sleep(0.05)
        completed_response = client.get(f"/rides/{ride_id}")
        if completed_response.json()["status"] == "ride-completed":
            break

    assert completed_response.status_code == 200
    assert completed_response.json()["status"] == "ride-completed"

    response = completed_response
    for _ in range(14):
        sleep(0.05)
        response = client.get(f"/rides/{ride_id}")
        if response.json()["status"] == "payment-confirmed":
            break

    assert response.status_code == 200
    assert response.json() == {
        "ride_id": ride_id,
        "status": "payment-confirmed",
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
            "capture_id": "cap-ride-1",
            "amount": 18.5,
            "currency": "EUR",
            "status": "captured",
        },
        "progress": {
            "phase": "ride-completed",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    }
