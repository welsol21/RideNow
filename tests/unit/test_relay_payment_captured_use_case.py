"""Unit tests for Notification relay of captured payments."""

from ridenow_notification.core.application.relay_payment_captured import (
    RelayPaymentCapturedUseCase,
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


async def test_notification_relays_payment_captured_to_broker() -> None:
    """Verify Notification turns PaymentCaptured into Broker-visible confirmation."""

    publisher = RecordingEventPublisher()
    use_case = RelayPaymentCapturedUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="payment",
            payload=DomainEventPayload(
                name="PaymentCaptured",
                data={
                    "ride_id": "ride-1",
                    "capture_id": "cap-ride-1",
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "notification"
    assert published.payload == DomainEventPayload(
        name="PaymentConfirmedVisible",
        data={
            "ride_id": "ride-1",
            "capture_id": "cap-ride-1",
        },
    )
