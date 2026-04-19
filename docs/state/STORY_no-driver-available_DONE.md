# Story Done - no-driver-available

## Acceptance Test

- `tests/acceptance/test_no_driver_available.py::test_no_driver_available_becomes_visible_to_the_customer`

## New Units And Adapters

- failure branch in `AssignDriverUseCase`
- `RelayNoDriverAvailableUseCase`
- `ApplyNoDriverAvailableUseCase`
- deterministic request trigger via `customer_id="customer-no-driver"`

## Prior Tests Still Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
