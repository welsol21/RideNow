"""Broker use case that applies inbound ETA updates."""

from ridenow_broker.core.application.ports import RideStatusStore
from ridenow_shared.events import EventEnvelope


class ApplyEtaUpdatedUseCase:
    """Update customer-visible ride state from an EtaUpdated event."""

    def __init__(self, status_store: RideStatusStore) -> None:
        """Store the ride-status persistence dependency."""

        self._status_store = status_store

    async def execute(self, event: EventEnvelope) -> None:
        """Persist customer-visible route and ETA feedback."""

        ride_id = str(event.payload.data["ride_id"])
        current_state = await self._status_store.get(ride_id) or {}
        next_state = dict(current_state)
        next_state["status"] = "eta-updated"
        next_state["route"] = {
            "distance_km": float(event.payload.data["distance_km"]),
            "pickup_eta_minutes": int(event.payload.data["pickup_eta_minutes"]),
            "trip_duration_minutes": int(event.payload.data["trip_duration_minutes"]),
        }
        await self._status_store.put(ride_id, next_state)
