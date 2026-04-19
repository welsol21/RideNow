"""Notification use case that relays driver assignments to the Route domain."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayRouteRequestUseCase:
    """Relay DriverAssigned outcomes into RouteRequested events."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish a RouteRequested event from a DriverAssigned input."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="RouteRequested",
                    data=dict(event.payload.data),
                ),
            )
        )
