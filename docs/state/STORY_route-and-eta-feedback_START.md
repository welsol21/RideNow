# Story Start - route-and-eta-feedback

## Acceptance Scenario

Write an acceptance test that creates a ride through the Broker,
observes the initial driver-assigned state, and then verifies that the
customer can observe route and ETA feedback through the customer-facing
read boundary once downstream Route processing completes.

## Ports Touched

- Broker inbound HTTP adapter
- Broker ride-status state store
- event publication and consumption boundaries between Driver, Notification, Route, and Broker

## Existing Tests Expected To Stay Green

- `tests/acceptance/test_health_check.py`
- `tests/acceptance/test_request_ride_acknowledgement.py`
- `tests/acceptance/test_driver_assigned.py`
- all green integration tests under `tests/integration/`
- all green contract tests under `tests/contracts/`
