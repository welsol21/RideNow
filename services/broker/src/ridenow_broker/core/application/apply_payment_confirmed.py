"""Broker use case that applies visible payment confirmation updates."""

from ridenow_broker.core.application.ports import RideStatusStore
from ridenow_shared.events import EventEnvelope


class ApplyPaymentConfirmedUseCase:
    """Update customer-visible ride state from a PaymentConfirmedVisible event."""

    def __init__(self, status_store: RideStatusStore) -> None:
        """Store the ride-status persistence dependency."""

        self._status_store = status_store

    async def execute(self, event: EventEnvelope) -> None:
        """Persist customer-visible payment confirmation feedback."""

        ride_id = str(event.payload.data["ride_id"])
        current_state = await self._status_store.get(ride_id) or {}
        next_state = dict(current_state)
        current_payment = current_state.get("payment")
        payment = dict(current_payment) if isinstance(current_payment, dict) else {}
        payment["capture_id"] = str(event.payload.data["capture_id"])
        payment["status"] = "captured"
        next_state["payment"] = payment
        next_state["status"] = "payment-confirmed"
        await self._status_store.put(ride_id, next_state)
