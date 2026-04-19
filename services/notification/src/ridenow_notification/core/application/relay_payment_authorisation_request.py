"""Notification use case that relays fare estimates to the Payment domain."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayPaymentAuthorisationRequestUseCase:
    """Relay FareEstimated outcomes into PaymentAuthorisationRequested events."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a payment-authorisation request from a fare estimate input."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="PaymentAuthorisationRequested",
                    data=dict(event.payload.data),
                ),
            )
        )
