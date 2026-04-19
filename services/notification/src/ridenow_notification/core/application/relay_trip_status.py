"""Notification use case that relays Tracking progress to the Broker boundary."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayTripStatusUseCase:
    """Relay TripStatusUpdated events into Broker-visible progress events."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a TripProgressVisible event from a trip-status update input."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="TripProgressVisible",
                    data=dict(event.payload.data),
                ),
            )
        )
