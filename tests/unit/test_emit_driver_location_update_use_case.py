"""Unit tests for Driver live-progress emission behaviour."""

from ridenow_driver.core.application.emit_driver_location_update import (
    EmitDriverLocationUpdateUseCase,
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


async def test_driver_service_emits_location_update_after_payment_authorisation() -> None:
    """Verify Driver starts trip progress updates after payment authorisation."""

    publisher = RecordingEventPublisher()
    use_case = EmitDriverLocationUpdateUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="payment",
            payload=DomainEventPayload(
                name="PaymentAuthorised",
                data={"ride_id": "ride-1"},
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "driver"
    assert published.payload == DomainEventPayload(
        name="DriverLocationUpdated",
        data={
            "ride_id": "ride-1",
            "driver_lat": 53.3472,
            "driver_lon": -6.2591,
        },
    )
