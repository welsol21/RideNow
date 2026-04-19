"""Unit tests for Notification relay of fare requests."""

from ridenow_notification.core.application.relay_fare_request import (
    RelayFareRequestUseCase,
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


async def test_notification_relays_eta_feedback_to_fare_request() -> None:
    """Verify Notification turns EtaUpdated into FareRequested."""

    publisher = RecordingEventPublisher()
    use_case = RelayFareRequestUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="route",
            payload=DomainEventPayload(
                name="EtaUpdated",
                data={
                    "ride_id": "ride-1",
                    "distance_km": 4.8,
                    "pickup_eta_minutes": 3,
                    "trip_duration_minutes": 11,
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "notification"
    assert published.payload == DomainEventPayload(
        name="FareRequested",
        data={
            "ride_id": "ride-1",
            "distance_km": 4.8,
            "pickup_eta_minutes": 3,
            "trip_duration_minutes": 11,
        },
    )
