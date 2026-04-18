"""In-memory state-store adapter for contract and integration tests."""

from typing import Generic, TypeVar

StateT = TypeVar("StateT")


class InMemoryStateStore(Generic[StateT]):
    """In-memory key/value store implementing the shared state-store contract.

    Parameters:
        None.
    Return value:
        State store instance backed by a local dictionary.
    Exceptions raised:
        None.
    Example:
        store = InMemoryStateStore[dict[str, object]]()
    """

    def __init__(self) -> None:
        """Initialise the internal state dictionary."""

        self._state: dict[str, StateT] = {}

    async def put(self, key: str, state: StateT) -> None:
        """Persist state by key in memory."""

        self._state[key] = state

    async def get(self, key: str) -> StateT | None:
        """Return stored state by key, or `None` if it is missing."""

        return self._state.get(key)
