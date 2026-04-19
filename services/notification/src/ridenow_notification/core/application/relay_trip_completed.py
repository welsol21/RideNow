"""Notification use case that relays trip completion outcomes."""

from ridenow_notification.core.application.ports import NotificationEventPublisher
from ridenow_shared.events import DomainEventPayload, EventEnvelope


class RelayTripCompletedUseCase:
    """Relay TripCompleted outcomes to Broker and Payment boundaries."""

    def __init__(self, event_publisher: NotificationEventPublisher) -> None:
        """Store the outbound event publisher dependency."""

        self._event_publisher = event_publisher

    async def execute(self, event: EventEnvelope) -> None:
        """Publish Broker-visible completion and payment capture request events."""

        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="RideCompletedVisible",
                    data=dict(event.payload.data),
                ),
            )
        )
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=event.correlation_id,
                source="notification",
                payload=DomainEventPayload(
                    name="PaymentCaptureRequested",
                    data={"ride_id": str(event.payload.data["ride_id"])},
                ),
            )
        )
