"""Notification use case that relays payment capture outcomes to Broker."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayPaymentCapturedUseCase:
    """Relay PaymentCaptured outcomes into Broker-visible confirmation events."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a payment confirmation event from a capture outcome input."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="PaymentConfirmedVisible",
                    data=dict(event.payload.data),
                ),
            )
        )
