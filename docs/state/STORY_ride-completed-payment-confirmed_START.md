# Story Start - ride-completed-payment-confirmed

## Acceptance Scenario

Write an acceptance test that creates a ride through the Broker,
observes trip progress, and then verifies that the customer can first
observe ride completion and then payment confirmation through the
customer-facing read boundary once downstream Tracking, Notification,
and Payment processing complete.

## Ports Touched

- Broker inbound HTTP adapter
- Broker ride-status state store
- event publication and consumption boundaries between Tracking, Notification, Payment, and Broker

## Existing Tests Expected To Stay Green

- `tests/acceptance/test_health_check.py`
- `tests/acceptance/test_request_ride_acknowledgement.py`
- `tests/acceptance/test_driver_assigned.py`
- `tests/acceptance/test_route_and_eta_feedback.py`
- `tests/acceptance/test_payment_authorised.py`
- `tests/acceptance/test_trip_progress.py`
- all green integration tests under `tests/integration/`
- all green contract tests under `tests/contracts/`
