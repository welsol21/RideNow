"""Notification use case that relays driver locations to Tracking."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayTrackingLocationUseCase:
    """Relay DriverLocationUpdated events into Tracking input events."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a TrackingLocationUpdated event from a driver location input."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="TrackingLocationUpdated",
                    data=dict(event.payload.data),
                ),
            )
        )
