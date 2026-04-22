"""Unit tests for Notification relay of trip completion."""

from ridenow_notification.core.application.relay_trip_completed import (
    RelayTripCompletedUseCase,
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


async def test_notification_relays_trip_completed_to_broker_and_payment() -> None:
    """Verify Notification relays trip completion to both Broker and Payment."""

    publisher = RecordingEventPublisher()
    use_case = RelayTripCompletedUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="tracking",
            payload=DomainEventPayload(
                name="TripCompleted",
                data={
                    "ride_id": "ride-1",
                    "driver_lat": 53.3472,
                    "driver_lon": -6.2591,
                },
            ),
        )
    )

    assert [event.payload.name for event in publisher.events] == [
        "RideCompletedVisible",
        "PaymentCaptureRequested",
    ]
    ride_completed_event, capture_request_event = publisher.events
    assert ride_completed_event.correlation_id == "ride-1"
    assert ride_completed_event.source == "notification"
    assert ride_completed_event.payload == DomainEventPayload(
        name="RideCompletedVisible",
        data={
            "ride_id": "ride-1",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    )
    assert capture_request_event.correlation_id == "ride-1"
    assert capture_request_event.source == "notification"
    assert capture_request_event.payload == DomainEventPayload(
        name="PaymentCaptureRequested",
        data={"ride_id": "ride-1"},
    )
