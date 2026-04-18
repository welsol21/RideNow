"""Request-ride use case for the Broker service."""

from dataclasses import dataclass

from ridenow_broker.core.application.ports import BrokerEventPublisher, RideStatusStore
from ridenow_shared.events import DomainEventPayload, EventEnvelope


@dataclass(frozen=True)
class RequestRideCommand:
    """Command payload for a customer ride request.

    Parameters:
        customer_id: Passenger identifier.
        pickup: Pickup coordinates and metadata.
        dropoff: Dropoff coordinates and metadata.
    Return value:
        Immutable command object passed to the use case.
    Exceptions raised:
        None.
    Example:
        RequestRideCommand(customer_id="customer-1", pickup={}, dropoff={})
    """

    customer_id: str
    pickup: dict[str, object]
    dropoff: dict[str, object]


@dataclass(frozen=True)
class RequestRideResult:
    """Customer-visible acknowledgement returned by the use case.

    Parameters:
        ride_id: Generated ride identifier.
        status: Customer-visible acknowledgement status.
    Return value:
        Immutable acknowledgement DTO.
    Exceptions raised:
        None.
    Example:
        RequestRideResult(ride_id="ride-1", status="request-submitted")
    """

    ride_id: str
    status: str


class RequestRideUseCase:
    """Use case that acknowledges a customer ride request.

    Parameters:
        status_store: Persistence port for customer-visible ride status.
        event_publisher: Event publication port for downstream collaboration.
    Return value:
        Use case instance capable of acknowledging ride requests.
    Exceptions raised:
        Storage or transport exceptions may propagate from dependencies.
    Example:
        result = await RequestRideUseCase(store, publisher).execute(command)
    """

    def __init__(
        self,
        status_store: RideStatusStore,
        event_publisher: BrokerEventPublisher,
    ) -> None:
        """Store the outbound dependencies used by the use case."""

        self._status_store = status_store
        self._event_publisher = event_publisher

    async def execute(self, command: RequestRideCommand) -> RequestRideResult:
        """Persist the initial ride state and publish a ride-request event."""

        ride_id = "ride-1"
        state = {
            "customer_id": command.customer_id,
            "status": "request-submitted",
            "pickup": command.pickup,
            "dropoff": command.dropoff,
        }
        await self._status_store.put(ride_id, state)
        await self._event_publisher.publish(
            EventEnvelope(
                correlation_id=ride_id,
                source="broker",
                payload=DomainEventPayload(
                    name="RideRequested",
                    data={
                        "ride_id": ride_id,
                        "customer_id": command.customer_id,
                        "pickup": command.pickup,
                        "dropoff": command.dropoff,
                    },
                ),
            )
        )
        return RequestRideResult(
            ride_id=ride_id,
            status="request-submitted",
        )
