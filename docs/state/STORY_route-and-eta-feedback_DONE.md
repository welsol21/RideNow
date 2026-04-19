# Story Done - route-and-eta-feedback

## Acceptance Test

- `tests/acceptance/test_route_and_eta_feedback.py::test_route_and_eta_feedback_become_visible_to_the_customer`

## New Units And Adapters

- `RelayRouteRequestUseCase`
- `CalculateRouteUseCase`
- `ApplyEtaUpdatedUseCase`
- Broker route payload in `GET /rides/{ride_id}`
- delayed in-memory event-bus wiring across Driver, Notification, Route, and Broker

## Prior Tests Still Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
