# Story Done - issue-submitted

## Acceptance Test

- `tests/acceptance/test_issue_submitted.py::test_issue_submission_returns_traceable_acknowledgement`

## New Units And Adapters

- `IssueSubmissionUseCase`
- Broker `POST /issues` HTTP adapter
- in-memory issue store wiring in Broker composition root

## Prior Tests Still Green

- `tests/acceptance`
- `tests/contracts`
- `tests/integration`
