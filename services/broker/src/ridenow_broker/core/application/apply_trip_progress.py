"""Broker use case that applies visible trip progress updates."""

from ridenow_broker.core.application.ports import RideStatusStore
from ridenow_shared.events import EventEnvelope


class ApplyTripProgressUseCase:
    """Update customer-visible ride state from a TripProgressVisible event."""

    def __init__(self, status_store: RideStatusStore) -> None:
        """Store the ride-status persistence dependency."""

        self._status_store = status_store

    async def execute(self, event: EventEnvelope) -> None:
        """Persist customer-visible trip-progress feedback."""

        ride_id = str(event.payload.data["ride_id"])
        current_state = await self._status_store.get(ride_id) or {}
        next_state = dict(current_state)
        next_state["status"] = "trip-in-progress"
        next_state["progress"] = {
            "phase": str(event.payload.data["phase"]),
            "driver_lat": float(event.payload.data["driver_lat"]),
            "driver_lon": float(event.payload.data["driver_lon"]),
        }
        await self._status_store.put(ride_id, next_state)
