"""Notification use case that relays ride requests to the Driver domain."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayDriverSearchUseCase:
    """Relay Broker ride requests into Driver search requests."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a DriverSearchRequested event from a RideRequested input."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="DriverSearchRequested",
                    data=dict(event.payload.data),
                ),
            )
        )
