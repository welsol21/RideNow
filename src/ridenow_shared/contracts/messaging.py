"""Messaging contracts shared by RideNow services."""

from collections.abc import Awaitable, Callable
from typing import Protocol

from ridenow_shared.events.models import EventEnvelope


class EventPublisher(Protocol):
    """Protocol for event publication.

    Parameters:
        event: Fully formed event envelope to publish.
    Return value:
        Awaitable completing when the event has been handed to the transport.
    Exceptions raised:
        Transport-specific exceptions may propagate from the implementation.
    Example:
        await publisher.publish(event)
    """

    async def publish(self, event: EventEnvelope) -> None:
        """Publish a shared event envelope."""


EventHandler = Callable[[EventEnvelope], Awaitable[None]]


class EventConsumer(Protocol):
    """Protocol for event subscription.

    Parameters:
        topic: Logical routing key or topic name.
        handler: Async callback invoked for each event on the topic.
    Return value:
        Awaitable completing when the subscription is active.
    Exceptions raised:
        Transport-specific exceptions may propagate from the implementation.
    Example:
        await consumer.subscribe("ride.requested", handler)
    """

    async def subscribe(self, topic: str, handler: EventHandler) -> None:
        """Subscribe a handler to the given topic."""
