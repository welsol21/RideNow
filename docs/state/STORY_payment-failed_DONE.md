# Story Done - payment-failed

## Acceptance Test

- `tests/acceptance/test_payment_failed.py::test_payment_failed_becomes_visible_to_the_customer`

## New Units And Adapters

- failure branch in `AuthorisePaymentUseCase`
- `RelayPaymentFailedUseCase`
- `ApplyPaymentFailedUseCase`
- deterministic request trigger via `customer_id="customer-payment-fail"`

## Prior Tests Still Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
