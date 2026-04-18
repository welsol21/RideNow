# Story Start - driver-assigned

## Acceptance Scenario

Write an acceptance test that creates a ride through the Broker and
then verifies that the customer can observe a driver-assigned state
with driver details through the customer-facing read boundary.

## Ports Touched

- Broker inbound HTTP adapter
- Broker ride-status state store
- event publication and consumption boundaries between Broker and Driver

## Existing Tests Expected To Stay Green

- `tests/acceptance/test_health_check.py`
- `tests/acceptance/test_request_ride_acknowledgement.py`
- all green integration tests under `tests/integration/`
- all green contract tests under `tests/contracts/`
