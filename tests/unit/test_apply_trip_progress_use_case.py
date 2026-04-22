"""Unit tests for Broker application of trip progress updates."""

from ridenow_broker.core.application.apply_trip_progress import ApplyTripProgressUseCase

from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingRideStatusStore:
    """Test double capturing persisted ride state."""

    def __init__(self, states: dict[str, dict[str, object]]) -> None:
        """Store initial ride state values."""

        self.saved = states

    async def put(self, key: str, state: dict[str, object]) -> None:
        """Persist ride state by key."""

        self.saved[key] = state

    async def get(self, key: str) -> dict[str, object] | None:
        """Return ride state by key if present."""

        return self.saved.get(key)


async def test_broker_applies_trip_progress_to_customer_visible_state() -> None:
    """Verify Broker updates stored ride state after visible trip progress."""

    store = RecordingRideStatusStore(
        {
            "ride-1": {
                "customer_id": "customer-1",
                "status": "payment-authorised",
                "pickup": {"lat": 53.3498, "lon": -6.2603},
                "dropoff": {"lat": 53.3440, "lon": -6.2672},
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
        }
    )
    use_case = ApplyTripProgressUseCase(status_store=store)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="TripProgressVisible",
                data={
                    "ride_id": "ride-1",
                    "phase": "driver-arriving",
                    "driver_lat": 53.3472,
                    "driver_lon": -6.2591,
                },
            ),
        )
    )

    assert store.saved["ride-1"] == {
        "customer_id": "customer-1",
        "status": "trip-in-progress",
        "pickup": {"lat": 53.3498, "lon": -6.2603},
        "dropoff": {"lat": 53.3440, "lon": -6.2672},
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
