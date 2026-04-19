"""Unit tests for Broker customer-visible ride-status reads."""

from ridenow_broker.core.application.ride_status import (
    GetRideStatusResult,
    GetRideStatusUseCase,
)


class RecordingRideStatusStore:
    """Test double returning preloaded ride states by identifier."""

    def __init__(self, states: dict[str, dict[str, object]]) -> None:
        """Store the preloaded ride states."""

        self._states = states

    async def put(self, key: str, state: dict[str, object]) -> None:
        """Persist a ride state in the local test double."""

        self._states[key] = state

    async def get(self, key: str) -> dict[str, object] | None:
        """Return a ride state by identifier if it exists."""

        return self._states.get(key)


async def test_get_ride_status_returns_customer_visible_driver_assignment() -> None:
    """Verify the Broker can return the stored driver-assigned ride state."""

    store = RecordingRideStatusStore(
        {
            "ride-1": {
                "status": "driver-assigned",
                "driver": {
                    "driver_id": "driver-1",
                    "vehicle_id": "vehicle-1",
                },
            }
        }
    )
    use_case = GetRideStatusUseCase(status_store=store)

    result = await use_case.execute("ride-1")

    assert result == GetRideStatusResult(
        ride_id="ride-1",
        status="driver-assigned",
        driver={
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
        },
    )
