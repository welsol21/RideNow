# Testing Strategy

RideNow uses top-down outside-in TDD and keeps multiple feedback loops.

## Test Layers

| Layer | Directory | Scope |
| --- | --- | --- |
| Unit | `tests/unit` | Small use cases, relays, and bootstrap helpers |
| Acceptance | `tests/acceptance` | Customer-visible Broker scenarios |
| Contracts | `tests/contracts` | Shared outbound adapter contracts |
| Integration | `tests/integration` | Service graph, adapters, and observability wiring |
| E2E | `tests/e2e` | Live Compose smoke checks |
| Non-functional | `tests/nonfunctional` | Performance, resilience, audit, monitoring |

## Development Flow

1. Start with a failing integration or acceptance test from the outside
2. Add the smallest failing unit test for the next missing internal slice
3. Write minimum production code
4. Return to the upper-level test until it passes
5. Keep all earlier green tests green

## Common Commands

Run unit tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/unit
```

Run acceptance tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/acceptance
```

Run contract and integration tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/contracts tests/integration
```

Run live E2E:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/e2e
```

Run non-functional suite:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/nonfunctional
```

Run the full gate:

```powershell
.\.venv\Scripts\python.exe -m ruff check src services tests
.\.venv\Scripts\python.exe -m mypy src services tests/nonfunctional
.\.venv\Scripts\python.exe -m pytest -q tests/unit tests/acceptance tests/contracts tests/integration tests/e2e tests/nonfunctional
```

## Coverage Target

- Branch coverage threshold: `95%`
- Coverage scope:
  - `src/ridenow_shared`
  - all seven service packages

## Adapter Verification

- Contract suites prove that in-memory and real adapters behave alike
- RabbitMQ roundtrip and PostgreSQL persistence tests validate real adapters
- E2E and non-functional suites validate Compose-hosted runtime behavior
