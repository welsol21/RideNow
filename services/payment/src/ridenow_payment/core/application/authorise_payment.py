"""Payment use case that emits deterministic payment authorisation outcomes."""

from ridenow_payment.core.application.ports import PaymentEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class AuthorisePaymentUseCase:
    """Authorise payment for an inbound payment request event."""

    def __init__(self, event_publisher: PaymentEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish deterministic payment authorisation for the requested ride."""

        ride_id = str(event.payload.data["ride_id"])
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="payment",
                payload=DomainEventPayload(
                    name="PaymentAuthorised",
                    data={
                        "ride_id": ride_id,
                        "authorisation_id": f"auth-{ride_id}",
                        "amount": float(event.payload.data["amount"]),
                        "currency": str(event.payload.data["currency"]),
                    },
                ),
            )
        )
