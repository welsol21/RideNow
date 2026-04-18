"""Outbound ports for the Payment service."""

from ridenow_shared.contracts import EventConsumer, EventPublisher, StateStore

PaymentStateStore = StateStore[dict[str, object]]
PaymentEventPublisher = EventPublisher
PaymentEventConsumer = EventConsumer

__all__ = [
    "PaymentEventConsumer",
    "PaymentEventPublisher",
    "PaymentStateStore",
]
