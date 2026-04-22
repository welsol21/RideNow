"""Unit tests for Notification relay of driver location updates."""

from ridenow_notification.core.application.relay_tracking_location import (
    RelayTrackingLocationUseCase,
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


async def test_notification_relays_driver_location_to_tracking() -> None:
    """Verify Notification turns DriverLocationUpdated into tracking input."""

    publisher = RecordingEventPublisher()
    use_case = RelayTrackingLocationUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="driver",
            payload=DomainEventPayload(
                name="DriverLocationUpdated",
                data={
                    "ride_id": "ride-1",
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
        name="TrackingLocationUpdated",
        data={
            "ride_id": "ride-1",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    )
