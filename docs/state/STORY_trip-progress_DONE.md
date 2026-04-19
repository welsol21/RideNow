# Story Done - trip-progress

## Acceptance Test

- `tests/acceptance/test_trip_progress.py::test_trip_progress_becomes_visible_to_the_customer`

## New Units And Adapters

- `EmitDriverLocationUpdateUseCase`
- `RelayTrackingLocationUseCase`
- `DeriveTripStatusUseCase`
- `RelayTripStatusUseCase`
- `ApplyTripProgressUseCase`
- Broker progress payload in `GET /rides/{ride_id}`
- delayed in-memory event-bus wiring across Driver, Notification, Tracking, and Broker

## Prior Tests Still Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
