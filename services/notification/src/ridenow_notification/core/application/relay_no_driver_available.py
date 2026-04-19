"""Notification use case that relays no-driver outcomes to Broker."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayNoDriverAvailableUseCase:
    """Relay NoDriverAvailable outcomes into Broker-visible failure events."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a Broker-visible no-driver failure event."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="NoDriverAvailableVisible",
                    data=dict(event.payload.data),
                ),
            )
        )
