"""Shared state-store contracts for RideNow services."""

from typing import Protocol, TypeVar


StateT = TypeVar("StateT")


class StateStore(Protocol[StateT]):
    """Protocol for durable state storage by identifier.

    Parameters:
        key: Stable identifier for the stored state.
        state: State value to persist.
    Return value:
        Implementations either return stored state or `None` for misses.
    Exceptions raised:
        Storage-specific exceptions may propagate from the implementation.
    Example:
        await store.put("ride-1", state)
    """

    async def put(self, key: str, state: StateT) -> None:
        """Persist state by key."""

    async def get(self, key: str) -> StateT | None:
        """Return stored state by key, or `None` if it is missing."""
