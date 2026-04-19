# Story Done - payment-authorised

## Acceptance Test

- `tests/acceptance/test_payment_authorised.py::test_payment_authorisation_becomes_visible_to_the_customer`

## New Units And Adapters

- `RelayFareRequestUseCase`
- `CalculateFareUseCase`
- `RelayPaymentAuthorisationRequestUseCase`
- `AuthorisePaymentUseCase`
- `ApplyPaymentAuthorisedUseCase`
- Broker payment payload in `GET /rides/{ride_id}`
- delayed in-memory event-bus wiring across Notification, Pricing, Payment, and Broker

## Prior Tests Still Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
