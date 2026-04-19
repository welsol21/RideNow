# Story Done - driver-assigned

## Acceptance Test

- `tests/acceptance/test_driver_assigned.py::test_driver_assignment_becomes_visible_to_the_customer`

## New Units And Adapters

- `GetRideStatusUseCase`
- `ApplyDriverAssignedUseCase`
- `RelayDriverSearchUseCase`
- `AssignDriverUseCase`
- Broker `GET /rides/{ride_id}` HTTP adapter
- in-memory event-bus wiring across Broker, Notification, and Driver

## Prior Tests Still Green

- `tests/acceptance/test_health_check.py::test_health_check_returns_ok`
- `tests/acceptance/test_request_ride_acknowledgement.py::test_request_ride_returns_customer_visible_acknowledgement`
- `tests/acceptance/test_driver_assigned.py::test_driver_assignment_becomes_visible_to_the_customer`
- `tests/contracts`
- `tests/integration`
