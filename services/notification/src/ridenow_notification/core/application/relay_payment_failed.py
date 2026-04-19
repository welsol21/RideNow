"""Notification use case that relays payment failures to Broker."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayPaymentFailedUseCase:
    """Relay PaymentFailed outcomes into Broker-visible failure events."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a Broker-visible payment failure event."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="PaymentFailedVisible",
                    data=dict(event.payload.data),
                ),
            )
        )
