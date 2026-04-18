"""Unit tests for the Broker request-ride use case."""

from ridenow_broker.core.application.request_ride import (
    RequestRideCommand,
    RequestRideResult,
    RequestRideUseCase,
)
from ridenow_shared.events import EventEnvelope


class RecordingRideStatusStore:
    """Test double capturing persisted ride status values."""

    def __init__(self) -> None:
        """Initialise the in-memory recording store."""

        self.saved: dict[str, dict[str, object]] = {}

    async def put(self, key: str, state: dict[str, object]) -> None:
        """Record state by ride identifier."""

        self.saved[key] = state

    async def get(self, key: str) -> dict[str, object] | None:
        """Return previously recorded state."""

        return self.saved.get(key)


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published envelope."""

        self.events.append(event)


async def test_request_ride_use_case_acknowledges_and_publishes() -> None:
    """Verify the use case persists visible status and publishes the request event."""

    store = RecordingRideStatusStore()
    publisher = RecordingEventPublisher()
    use_case = RequestRideUseCase(status_store=store, event_publisher=publisher)

    result = await use_case.execute(
        RequestRideCommand(
            customer_id="customer-1",
            pickup={"lat": 53.3498, "lon": -6.2603},
            dropoff={"lat": 53.3440, "lon": -6.2672},
        )
    )

    assert result == RequestRideResult(
        ride_id="ride-1",
        status="request-submitted",
    )
    assert store.saved == {
        "ride-1": {
            "customer_id": "customer-1",
            "status": "request-submitted",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        }
    }
    assert len(publisher.events) == 1
    assert publisher.events[0].payload.name == "RideRequested"
    assert publisher.events[0].payload.data == {
        "ride_id": "ride-1",
        "customer_id": "customer-1",
        "pickup": {"lat": 53.3498, "lon": -6.2603},
        "dropoff": {"lat": 53.3440, "lon": -6.2672},
    }
