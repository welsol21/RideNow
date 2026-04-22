"""Customer-visible ride-status query use case for the Broker service."""

from dataclasses import dataclass

from ridenow_broker.core.application.ports import RideStatusStore


def _payload_or_none(value: object) -> dict[str, object] | None:
    """Return customer-visible payloads only when they are dictionaries."""

    return value if isinstance(value, dict) else None


@dataclass(frozen=True)
class GetRideStatusResult:
    """Customer-visible ride status returned by the Broker read boundary."""

    ride_id: str
    status: str
    driver: dict[str, object] | None = None
    route: dict[str, object] | None = None
    payment: dict[str, object] | None = None
    progress: dict[str, object] | None = None


class GetRideStatusUseCase:
    """Use case that returns customer-visible ride status by ride identifier."""

    def __init__(self, status_store: RideStatusStore) -> None:
        """Store the ride-status persistence dependency."""

        self._status_store = status_store

    async def execute(self, ride_id: str) -> GetRideStatusResult | None:
        """Return stored customer-visible ride status if the ride exists."""

        state = await self._status_store.get(ride_id)
        if state is None:
            return None
        return GetRideStatusResult(
            ride_id=ride_id,
            status=str(state["status"]),
            driver=_payload_or_none(state.get("driver")),
            route=_payload_or_none(state.get("route")),
            payment=_payload_or_none(state.get("payment")),
            progress=_payload_or_none(state.get("progress")),
        )
