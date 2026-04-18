"""Outbound ports for the Tracking service."""

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore

TrackingStateStore = StateStore[dict[str, object]]
TrackingEventPublisher = EventPublisher
TrackingEventConsumer = EventConsumer

__all__ = [
    "TrackingEventConsumer",
    "TrackingEventPublisher",
    "TrackingStateStore",
]
