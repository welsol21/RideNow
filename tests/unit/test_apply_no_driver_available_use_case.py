"""Unit tests for Broker application of no-driver outcomes."""

from ridenow_broker.core.application.apply_no_driver_available import (
    ApplyNoDriverAvailableUseCase,
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


async def test_broker_applies_no_driver_available_to_customer_visible_state() -> None:
    """Verify Broker updates stored ride state after a no-driver outcome."""

    store = RecordingRideStatusStore(
        {
            "ride-1": {
                "customer_id": "customer-no-driver",
                "status": "request-submitted",
                "pickup": {"lat": 53.3498, "lon": -6.2603},
                "dropoff": {"lat": 53.3440, "lon": -6.2672},
            }
        }
    )
    use_case = ApplyNoDriverAvailableUseCase(status_store=store)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="NoDriverAvailableVisible",
                data={"ride_id": "ride-1"},
            ),
        )
    )

    assert store.saved["ride-1"] == {
        "customer_id": "customer-no-driver",
        "status": "no-driver-available",
        "pickup": {"lat": 53.3498, "lon": -6.2603},
        "dropoff": {"lat": 53.3440, "lon": -6.2672},
    }
