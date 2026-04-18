"""Outbound ports for the Broker service."""

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore
from ridenow_shared.events import EventEnvelope


RideStatusStore = StateStore[dict[str, object]]
IssueStore = StateStore[dict[str, object]]
BrokerEventPublisher = EventPublisher
BrokerEventConsumer = EventConsumer

__all__ = [
    "BrokerEventConsumer",
    "BrokerEventPublisher",
    "EventEnvelope",
    "IssueStore",
    "RideStatusStore",
]
