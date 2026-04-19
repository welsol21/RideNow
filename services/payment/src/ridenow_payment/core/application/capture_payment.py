"""Payment use case that emits deterministic payment capture outcomes."""

from ridenow_payment.core.application.ports import PaymentEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class CapturePaymentUseCase:
    """Capture payment for a completed ride."""

    def __init__(self, event_publisher: PaymentEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish deterministic payment capture for the requested ride."""

        ride_id = str(event.payload.data["ride_id"])
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="payment",
                payload=DomainEventPayload(
                    name="PaymentCaptured",
                    data={
                        "ride_id": ride_id,
                        "capture_id": f"cap-{ride_id}",
                    },
                ),
            )
        )
