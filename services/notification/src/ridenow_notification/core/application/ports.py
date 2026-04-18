"""Outbound ports for the Notification service."""

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore

NotificationDeliveryStore = StateStore[dict[str, object]]
NotificationEventPublisher = EventPublisher
NotificationEventConsumer = EventConsumer

__all__ = [
    "NotificationDeliveryStore",
    "NotificationEventConsumer",
    "NotificationEventPublisher",
]
