# Story Done - request-ride-acknowledgement

## Acceptance Test

- `tests/acceptance/test_request_ride_acknowledgement.py::test_request_ride_returns_customer_visible_acknowledgement`

## New Units And Adapters

- `RequestRideUseCase`
- `RequestRideCommand`
- `RequestRideResult`
- Broker `POST /rides` HTTP adapter
- in-memory request-ride wiring in Broker composition root

## Prior Acceptance Tests Still Green

- `tests/acceptance/test_health_check.py::test_health_check_returns_ok`
- `tests/acceptance/test_request_ride_acknowledgement.py::test_request_ride_returns_customer_visible_acknowledgement`
