# Story Start - payment-authorised

## Acceptance Scenario

Write an acceptance test that creates a ride through the Broker,
observes the route and ETA feedback, and then verifies that the
customer can observe a payment-authorised state through the
customer-facing read boundary once downstream Pricing and Payment
processing complete.

## Ports Touched

- Broker inbound HTTP adapter
- Broker ride-status state store
- event publication and consumption boundaries between Route, Notification, Pricing, Payment, and Broker

## Existing Tests Expected To Stay Green

- `tests/acceptance/test_health_check.py`
- `tests/acceptance/test_request_ride_acknowledgement.py`
- `tests/acceptance/test_driver_assigned.py`
- `tests/acceptance/test_route_and_eta_feedback.py`
- all green integration tests under `tests/integration/`
- all green contract tests under `tests/contracts/`
