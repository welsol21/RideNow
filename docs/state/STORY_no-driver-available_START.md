# Story Start - no-driver-available

## Acceptance Scenario

Write an acceptance test that creates a ride through the Broker for a
request with no available driver and then verifies that the customer
can observe the terminal `no-driver-available` state through the
customer-facing read boundary.

## Ports Touched

- Broker inbound HTTP adapter
- Broker ride-status state store
- event publication and consumption boundaries between Broker, Notification, Driver, and Broker

## Existing Tests Expected To Stay Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
