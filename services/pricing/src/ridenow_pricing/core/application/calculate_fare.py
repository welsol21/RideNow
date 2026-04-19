"""Pricing use case that emits deterministic fare estimates."""

from ridenow_pricing.core.application.ports import PricingEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class CalculateFareUseCase:
    """Calculate customer-visible fare estimates."""

    def __init__(self, event_publisher: PricingEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish deterministic fare feedback for the requested ride."""

        ride_id = str(event.payload.data["ride_id"])
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="pricing",
                payload=DomainEventPayload(
                    name="FareEstimated",
                    data={
                        "ride_id": ride_id,
                        "amount": 18.5,
                        "currency": "EUR",
                    },
                ),
            )
        )
