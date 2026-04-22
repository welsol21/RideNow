"""Unit tests for Notification relay of payment failures."""

from ridenow_notification.core.application.relay_payment_failed import (
    RelayPaymentFailedUseCase,
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


async def test_notification_relays_payment_failed_to_broker() -> None:
    """Verify Notification forwards payment failure to the Broker boundary."""

    publisher = RecordingEventPublisher()
    use_case = RelayPaymentFailedUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="payment",
            payload=DomainEventPayload(
                name="PaymentFailed",
                data={"ride_id": "ride-1"},
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "notification"
    assert published.payload == DomainEventPayload(
        name="PaymentFailedVisible",
        data={"ride_id": "ride-1"},
    )
