"""Unit tests for Broker application of DriverAssigned outcomes."""

from ridenow_broker.core.application.apply_driver_assigned import (
    ApplyDriverAssignedUseCase,
)

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


async def test_broker_applies_driver_assignment_to_customer_visible_state() -> None:
    """Verify Broker updates stored ride state after DriverAssigned."""

    store = RecordingRideStatusStore(
        {
            "ride-1": {
                "customer_id": "customer-1",
                "status": "request-submitted",
                "pickup": {"lat": 53.3498, "lon": -6.2603},
                "dropoff": {"lat": 53.3440, "lon": -6.2672},
            }
        }
    )
    use_case = ApplyDriverAssignedUseCase(status_store=store)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="driver",
            payload=DomainEventPayload(
                name="DriverAssigned",
                data={
                    "ride_id": "ride-1",
                    "driver_id": "driver-1",
                    "vehicle_id": "vehicle-1",
                },
            ),
        )
    )

    assert store.saved["ride-1"] == {
        "customer_id": "customer-1",
        "status": "driver-assigned",
        "pickup": {"lat": 53.3498, "lon": -6.2603},
        "dropoff": {"lat": 53.3440, "lon": -6.2672},
        "driver": {
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
    }
