"""Outbound ports for the Route service."""

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore


RouteStateStore = StateStore[dict[str, object]]
RouteEventPublisher = EventPublisher
RouteEventConsumer = EventConsumer

__all__ = [
    "RouteEventConsumer",
    "RouteEventPublisher",
    "RouteStateStore",
]
