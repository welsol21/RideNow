# Story Start - request-ride-acknowledgement

## Acceptance Scenario

Write an acceptance test that submits a ride request through the Broker
public HTTP boundary and expects:

- HTTP `202 Accepted`
- generated `ride_id`
- immediate customer-visible status acknowledging the request

## Ports Touched

- Broker inbound HTTP adapter
- Broker ride-status state store
- Broker event publisher

## Existing Tests Expected To Stay Green

- `tests/acceptance/test_health_check.py`
- `tests/integration/test_full_system_startup_readiness.py`
- `tests/integration/test_full_system_happy_path_connectivity.py`
- `tests/integration/test_full_system_failure_path_connectivity.py`
- `tests/integration/test_manual_demo_mode.py`
- all contract tests under `tests/contracts/`
