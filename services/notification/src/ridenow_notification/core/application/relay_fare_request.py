"""Notification use case that relays ETA updates to the Pricing domain."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayFareRequestUseCase:
    """Relay EtaUpdated outcomes into FareRequested events."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a FareRequested event from an EtaUpdated input."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="FareRequested",
                    data=dict(event.payload.data),
                ),
            )
        )
