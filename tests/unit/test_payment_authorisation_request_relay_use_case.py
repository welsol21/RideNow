"""Unit tests for Notification relay of payment authorisation requests."""

from ridenow_notification.core.application.relay_payment_authorisation_request import (
    RelayPaymentAuthorisationRequestUseCase,
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


async def test_notification_relays_fare_estimate_to_payment_authorisation_request(
) -> None:
    """Verify Notification turns FareEstimated into PaymentAuthorisationRequested."""

    publisher = RecordingEventPublisher()
    use_case = RelayPaymentAuthorisationRequestUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="pricing",
            payload=DomainEventPayload(
                name="FareEstimated",
                data={
                    "ride_id": "ride-1",
                    "amount": 18.5,
                    "currency": "EUR",
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "notification"
    assert published.payload == DomainEventPayload(
        name="PaymentAuthorisationRequested",
        data={
            "ride_id": "ride-1",
            "amount": 18.5,
            "currency": "EUR",
        },
    )
