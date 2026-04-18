"""Outbound ports for the Driver service."""

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore

DriverStateStore = StateStore[dict[str, object]]
DriverEventPublisher = EventPublisher
DriverEventConsumer = EventConsumer

__all__ = [
    "DriverEventConsumer",
    "DriverEventPublisher",
    "DriverStateStore",
]
