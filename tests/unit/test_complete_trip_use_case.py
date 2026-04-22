"""Unit tests for Tracking trip completion behaviour."""

from ridenow_tracking.core.application.complete_trip import CompleteTripUseCase

from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_tracking_service_publishes_trip_completed() -> None:
    """Verify Tracking publishes deterministic trip completion."""

    publisher = RecordingEventPublisher()
    use_case = CompleteTripUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="TrackingLocationUpdated",
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
    assert published.source == "tracking"
    assert published.payload == DomainEventPayload(
        name="TripCompleted",
        data={
            "ride_id": "ride-1",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    )
