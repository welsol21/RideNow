"""Broker use case that applies inbound payment authorisation outcomes."""

from ridenow_broker.core.application.ports import RideStatusStore
from ridenow_shared.events import EventEnvelope


class ApplyPaymentAuthorisedUseCase:
    """Update customer-visible ride state from a PaymentAuthorised event."""

    def __init__(self, status_store: RideStatusStore) -> None:
        """Store the ride-status persistence dependency."""

        self._status_store = status_store

    async def execute(self, event: EventEnvelope) -> None:
        """Persist customer-visible payment authorisation feedback."""

        ride_id = str(event.payload.data["ride_id"])
        current_state = await self._status_store.get(ride_id) or {}
        next_state = dict(current_state)
        next_state["status"] = "payment-authorised"
        next_state["payment"] = {
            "authorisation_id": str(event.payload.data["authorisation_id"]),
            "amount": float(event.payload.data["amount"]),
            "currency": str(event.payload.data["currency"]),
        }
        await self._status_store.put(ride_id, next_state)
