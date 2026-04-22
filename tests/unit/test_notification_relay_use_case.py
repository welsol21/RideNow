"""Unit tests for Notification relay behaviour."""

from ridenow_notification.core.application.relay_driver_search import (
    RelayDriverSearchUseCase,
)

from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_notification_relays_ride_request_to_driver_search() -> None:
    """Verify Notification turns RideRequested into DriverSearchRequested."""

    publisher = RecordingEventPublisher()
    use_case = RelayDriverSearchUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="broker",
            payload=DomainEventPayload(
                name="RideRequested",
                data={
                    "ride_id": "ride-1",
                    "customer_id": "customer-1",
                    "pickup": {"lat": 53.3498, "lon": -6.2603},
                    "dropoff": {"lat": 53.3440, "lon": -6.2672},
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "notification"
    assert published.payload == DomainEventPayload(
        name="DriverSearchRequested",
        data={
            "ride_id": "ride-1",
            "customer_id": "customer-1",
            "pickup": {"lat": 53.3498, "lon": -6.2603},
            "dropoff": {"lat": 53.3440, "lon": -6.2672},
        },
    )
