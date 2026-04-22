"""Unit tests for Notification relay of trip-status updates."""

from ridenow_notification.core.application.relay_trip_status import (
    RelayTripStatusUseCase,
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


async def test_notification_relays_trip_status_to_broker() -> None:
    """Verify Notification forwards trip status to the Broker boundary."""

    publisher = RecordingEventPublisher()
    use_case = RelayTripStatusUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="tracking",
            payload=DomainEventPayload(
                name="TripStatusUpdated",
                data={
                    "ride_id": "ride-1",
                    "phase": "driver-arriving",
                    "driver_lat": 53.3472,
                    "driver_lon": -6.2591,
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "notification"
    assert published.payload == DomainEventPayload(
        name="TripProgressVisible",
        data={
            "ride_id": "ride-1",
            "phase": "driver-arriving",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    )
