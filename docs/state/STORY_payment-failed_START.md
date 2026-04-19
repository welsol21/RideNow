# Story Start - payment-failed

## Acceptance Scenario

Write an acceptance test that creates a ride through the Broker for a
request whose payment authorisation fails and then verifies that the
customer can observe the terminal `payment-failed` state through the
customer-facing read boundary.

## Ports Touched

- Broker inbound HTTP adapter
- Broker ride-status state store
- event publication and consumption boundaries between Route, Pricing, Payment, Notification, and Broker

## Existing Tests Expected To Stay Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
