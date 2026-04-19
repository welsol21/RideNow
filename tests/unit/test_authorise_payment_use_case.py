"""Unit tests for Payment authorisation behaviour."""

from ridenow_payment.core.application.authorise_payment import AuthorisePaymentUseCase
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RecordingEventPublisher:
    """Test double capturing published envelopes."""

    def __init__(self) -> None:
        """Initialise the in-memory event capture list."""

        self.events: list[EventEnvelope] = []

    async def publish(self, event: EventEnvelope) -> None:
        """Record a published event."""

        self.events.append(event)


async def test_payment_service_publishes_payment_authorised() -> None:
    """Verify Payment publishes deterministic authorisation outcome."""

    publisher = RecordingEventPublisher()
    use_case = AuthorisePaymentUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="PaymentAuthorisationRequested",
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
    assert published.source == "payment"
    assert published.payload == DomainEventPayload(
        name="PaymentAuthorised",
        data={
            "ride_id": "ride-1",
            "authorisation_id": "auth-ride-1",
            "amount": 18.5,
            "currency": "EUR",
        },
    )


async def test_payment_service_can_publish_payment_failed() -> None:
    """Verify Payment emits the payment-failed outcome for deterministic failure input."""

    publisher = RecordingEventPublisher()
    use_case = AuthorisePaymentUseCase(event_publisher=publisher)

    await use_case.execute(
        EventEnvelope(
            correlation_id="ride-1",
            source="notification",
            payload=DomainEventPayload(
                name="PaymentAuthorisationRequested",
                data={
                    "ride_id": "ride-1",
                    "amount": 18.5,
                    "currency": "EUR",
                    "customer_id": "customer-payment-fail",
                },
            ),
        )
    )

    assert len(publisher.events) == 1
    published = publisher.events[0]
    assert published.correlation_id == "ride-1"
    assert published.source == "payment"
    assert published.payload == DomainEventPayload(
        name="PaymentFailed",
        data={"ride_id": "ride-1"},
    )
