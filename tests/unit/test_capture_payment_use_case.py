"""Unit tests for Payment capture behaviour."""

from ridenow_payment.core.application.capture_payment import CapturePaymentUseCase
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_payment_service_publishes_payment_captured() -> None:
    """Verify Payment publishes deterministic capture outcome."""

    publisher = RecordingEventPublisher()
    use_case = CapturePaymentUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="PaymentCaptureRequested",
                data={"ride_id": "ride-1"},
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "payment"
    assert published.payload == DomainEventPayload(
        name="PaymentCaptured",
        data={
            "ride_id": "ride-1",
            "capture_id": "cap-ride-1",
        },
    )
