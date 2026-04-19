# Story Done - ride-completed-payment-confirmed

## Acceptance Test

- `tests/acceptance/test_ride_completed_payment_confirmed.py::test_ride_completion_and_payment_confirmation_become_visible`

## New Units And Adapters

- `CompleteTripUseCase`
- `RelayTripCompletedUseCase`
- `CapturePaymentUseCase`
- `RelayPaymentCapturedUseCase`
- `ApplyRideCompletedUseCase`
- `ApplyPaymentConfirmedUseCase`
- Broker payment payload now supports captured-payment details
- delayed in-memory finalisation wiring across Tracking, Notification, Payment, and Broker

## Prior Tests Still Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
