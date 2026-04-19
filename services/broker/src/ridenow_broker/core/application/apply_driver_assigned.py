"""Broker use case that applies inbound DriverAssigned outcomes."""

from ridenow_broker.core.application.ports import RideStatusStore
from ridenow_shared.events import EventEnvelope


class ApplyDriverAssignedUseCase:
    """Update customer-visible ride state from a DriverAssigned event."""

    def __init__(self, status_store: RideStatusStore) -> None:
        """Store the ride-status persistence dependency."""

        self._status_store = status_store

    async def execute(self, event: EventEnvelope) -> None:
        """Persist the customer-visible driver assignment outcome."""

        ride_id = str(event.payload.data["ride_id"])
        current_state = await self._status_store.get(ride_id) or {}
        next_state = dict(current_state)
        next_state["status"] = "driver-assigned"
        next_state["driver"] = {
            "driver_id": str(event.payload.data["driver_id"]),
            "vehicle_id": str(event.payload.data["vehicle_id"]),
        }
        await self._status_store.put(ride_id, next_state)
