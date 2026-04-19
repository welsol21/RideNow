# Story Start - issue-submitted

## Acceptance Scenario

Write an acceptance test that submits an issue through the Broker and
then verifies that the customer immediately receives a traceable issue
identifier and the `issue-submitted` acknowledgement.

## Ports Touched

- Broker inbound HTTP adapter
- Broker issue state store
- Broker event publication boundary

## Existing Tests Expected To Stay Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
