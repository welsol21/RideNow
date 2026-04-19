"""Broker use case that applies visible no-driver outcomes."""

from ridenow_broker.core.application.ports import RideStatusStore
from ridenow_shared.events import EventEnvelope


class ApplyNoDriverAvailableUseCase:
    """Update customer-visible ride state from a no-driver failure event."""

    def __init__(self, status_store: RideStatusStore) -> None:
        """Store the ride-status persistence dependency."""

        self._status_store = status_store

    async def execute(self, event: EventEnvelope) -> None:
        """Persist customer-visible no-driver failure feedback."""

        ride_id = str(event.payload.data["ride_id"])
        current_state = await self._status_store.get(ride_id) or {}
        next_state = dict(current_state)
        next_state["status"] = "no-driver-available"
        next_state.pop("driver", None)
        next_state.pop("route", None)
        next_state.pop("payment", None)
        next_state.pop("progress", None)
        await self._status_store.put(ride_id, next_state)
