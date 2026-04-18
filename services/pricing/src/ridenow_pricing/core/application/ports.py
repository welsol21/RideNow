"""Outbound ports for the Pricing service."""

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore

PricingStateStore = StateStore[dict[str, object]]
PricingEventPublisher = EventPublisher
PricingEventConsumer = EventConsumer

__all__ = [
    "PricingEventConsumer",
    "PricingEventPublisher",
    "PricingStateStore",
]
