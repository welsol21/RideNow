"""In-memory messaging adapters for contract and integration tests."""

from collections import defaultdict
from collections.abc import Awaitable, Callable

from ridenow_shared.events import EventEnvelope

EventHandler = Callable[[EventEnvelope], Awaitable[None]]


class InMemoryEventPublisher:
    """In-memory event publisher storing emitted envelopes in a list.

    Parameters:
        sink: Mutable list receiving published event envelopes.
    Return value:
        Publisher instance compatible with the shared event-publisher contract.
    Exceptions raised:
        None.
    Example:
        publisher = InMemoryEventPublisher(events)
    """

    def __init__(self, sink: list[EventEnvelope]) -> None:
        """Store the event sink used by the publisher."""

        self._sink = sink

    async def publish(self, event: EventEnvelope) -> None:
        """Append the event envelope to the configured sink."""

        self._sink.append(event)


class InMemoryEventBus:
    """In-memory event bus implementing publish and subscribe semantics.

    Parameters:
        None.
    Return value:
        Bus instance that can subscribe handlers and publish by topic.
    Exceptions raised:
        None.
    Example:
        bus = InMemoryEventBus()
    """

    def __init__(self) -> None:
        """Initialise an empty topic-handler registry."""

        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    async def subscribe(self, topic: str, handler: EventHandler) -> None:
        """Register a handler for the given topic."""

        self._handlers[topic].append(handler)

    async def publish(self, event: EventEnvelope) -> None:
        """Publish an event using its payload name as the topic."""

        await self.publish_to_topic(event.payload.name, event)

    async def publish_to_topic(self, topic: str, event: EventEnvelope) -> None:
        """Publish an event to a specific topic."""

        for handler in self._handlers[topic]:
            await handler(event)
