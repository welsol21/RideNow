# RideNow

RideNow is a multi-service ride-hailing platform implemented in a single
repository. The runtime topology contains seven collaborating services:

- `broker`
- `driver`
- `route`
- `pricing`
- `payment`
- `tracking`
- `notification`

The system is built around a public Broker API, RabbitMQ-based
service-to-service messaging, PostgreSQL-backed Broker state, and a
Compose-hosted demo stack with monitoring.

## What Is Implemented

- Public customer API through `broker`
  - `GET /health`
  - `GET /ready`
  - `GET /metrics`
  - `POST /rides`
  - `GET /rides/{ride_id}`
  - `POST /issues`
- Real service collaboration across all seven services
  - `RideRequested -> DriverSearchRequested -> DriverAssigned`
  - `DriverAssigned -> RouteRequested -> EtaUpdated`
  - `EtaUpdated -> FareRequested -> FareEstimated`
  - `FareEstimated -> PaymentAuthorisationRequested -> PaymentAuthorised`
  - `PaymentAuthorised -> DriverLocationUpdated -> TrackingLocationUpdated`
  - `TrackingLocationUpdated -> TripStatusUpdated -> TripProgressVisible`
  - `TripCompleted -> RideCompletedVisible -> PaymentCaptureRequested`
  - `PaymentCaptured -> PaymentConfirmedVisible`
- Failure paths
  - `no-driver-available`
  - `payment-failed`
- Secondary inbound adapter
  - `ridenow-broker` CLI with `health`, `request-ride`, and `submit-issue`
- Observability
  - JSON request logs
  - Prometheus metrics
  - Compose Prometheus target scraping for all seven services

## Repository Layout

- `services/` - service-specific code and composition roots
- `src/ridenow_shared/` - shared events, adapters, config, metrics, logging
- `tests/` - unit, acceptance, contracts, integration, e2e, nonfunctional
- `infra/compose/` - local multi-service stack and Prometheus config
- `infra/kubernetes/` - Kubernetes manifests for the seven services plus dependencies
- `docs/` - architecture, operations, guides, and state docs

## Possible Scaling

The current codebase is intentionally small enough to stay teachable and
testable, but several parts are structured for later expansion:

- Empty or near-empty `core/domain/` packages in several services are
  reserved for future domain entities, value objects, and policy logic.
  Right now much of the service behaviour fits in application use cases,
  so creating rich domain models everywhere would be scaffolding without
  payoff.
- Minimal `adapters/` packages in services such as `driver`, `route`,
  `pricing`, `payment`, `tracking`, and `notification` reflect the fact
  that their real runtime integration is currently assembled in
  `bootstrap/app.py` plus shared RabbitMQ adapters under
  `src/ridenow_shared/adapters/`. If a service later grows new inbound
  APIs, persistence, third-party integrations, or service-local
  observability hooks, that code belongs in its own `adapters/` package.
- `src/ridenow_shared/` centralises infrastructure that is identical
  across services today. If one service later needs a materially
  different transport, persistence pattern, or adapter policy, that logic
  can be moved from shared code into a service-local adapter without
  changing the external event contracts.
- Shared adapter code does not mean one shared runtime instance across
  the whole system. Each service still creates and owns its own runtime
  objects in its own `bootstrap/app.py`, including its own RabbitMQ
  publisher and consumer instances.
- Most non-Broker services are stateless in the current scope. If the
  platform later requires service-owned persistence, each service already
  has an isolated package boundary and deployment unit that can take on
  its own datastore and migrations independently.
- Demo behaviour is deterministic by design, for example
  `customer-no-driver` and `customer-payment-fail`. These are deliberate
  testability seams, not production policy. A more realistic version
  would replace them with real eligibility, routing, pricing, and payment
  decision logic behind the same service boundaries.

| Aspect | Current implementation | Why | Possible next step |
| --- | --- | --- | --- |
| Runtime boundary | Separate runtime service per domain | Required by the assignment and preserved in the final topology | Keep as is |
| Ports and application layer | Present per service | Supports the hexagonal structure and keeps business logic away from framework code | Enrich as service logic grows |
| Service-local adapters | Minimal outside `broker` | Current flows do not need richer per-service inbound/outbound surfaces yet | Add service-specific HTTP, persistence, or third-party adapters |
| Persistence | Mainly Broker-owned | Other services are mostly stateless in the current scope | Add service-owned datastores where long-lived state appears |
| Shared infrastructure code | Centralised in `src/ridenow_shared/` | Avoids repeating identical RabbitMQ, logging, metrics, and config boilerplate | Split out when a service needs materially different adapter behaviour |
| Domain layer depth | Light in several services | Current behaviour is simple enough to stay in use-case code | Add richer entities, value objects, and policy rules as complexity grows |

## Tech Stack

- Python 3.12+
- FastAPI
- RabbitMQ
- PostgreSQL
- Prometheus
- pytest, ruff, mypy, mkdocs-material

## Quick Start

1. Create and activate a virtual environment.
2. Install the project with dev and docs extras.
3. Start the full local stack with one command.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -e ".[dev,docs,nonfunctional]"
.\scripts\start.ps1
```

Probe the Broker:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/health"
Invoke-RestMethod "http://127.0.0.1:8001/ready"
```

## Manual Testing

There are two supported shell styles for manual testing:

- `PowerShell` with `Invoke-RestMethod`
- `Git Bash` with real `curl`

Do not mix them:

- PowerShell does not accept bash-style `curl -X/-H/-d` examples reliably
- Git Bash does not use PowerShell line continuation

### PowerShell

Create a ride:

```powershell
$body = @{
  customer_id = "customer-demo"
  pickup = @{
    lat = 53.3498
    lon = -6.2603
  }
  dropoff = @{
    lat = 53.3440
    lon = -6.2672
  }
} | ConvertTo-Json -Depth 5

$response = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8001/rides" `
  -ContentType "application/json" `
  -Body $body

$response
```

Read current customer-visible state:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/rides/<ride_id>"
```

Submit an issue:

```powershell
$issueBody = @{
  ride_id = "<ride_id>"
  customer_id = "customer-demo"
  category = "payment"
  description = "Manual verification follow-up."
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8001/issues" `
  -ContentType "application/json" `
  -Body $issueBody
```

### Git Bash

Run the helper script:

```bash
./scripts/integration_manual_test.sh health
./scripts/integration_manual_test.sh happy
./scripts/integration_manual_test.sh no-driver
./scripts/integration_manual_test.sh payment-fail
./scripts/integration_manual_test.sh trace happy
./scripts/integration_manual_test.sh issue <ride_id>
./scripts/integration_manual_test.sh all
```

Or use raw `curl`:

```bash
curl -X POST "http://127.0.0.1:8001/rides" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"customer-demo","pickup":{"lat":53.3498,"lon":-6.2603},"dropoff":{"lat":53.3440,"lon":-6.2672}}'
```

Demo customer ids:

- `customer-demo` -> happy path
- `customer-no-driver` -> terminal `no-driver-available`
- `customer-payment-fail` -> terminal `payment-failed`

For full request/response examples, trace mode, and manual scenario
order, see `docs/guides/manual_integration_testing.md`.

Stop the stack:

```powershell
.\scripts\stop.ps1
```

## Test Matrix

- Fast acceptance feedback

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/acceptance
```

- Contract and integration coverage

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/contracts tests/integration
```

- End-to-end and non-functional verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/e2e tests/nonfunctional
```

- Full gate

```powershell
.\.venv\Scripts\python.exe -m ruff check src services tests
.\.venv\Scripts\python.exe -m mypy src services tests/nonfunctional
.\.venv\Scripts\python.exe -m pytest -q tests/unit tests/acceptance tests/contracts tests/integration tests/e2e tests/nonfunctional
```

## Documentation

Recommended reading order:

1. `docs/guides/running_locally.md`
2. `docs/guides/manual_integration_testing.md`
3. `docs/architecture/overview.md`
4. `docs/architecture/service_catalogue.md`
5. `docs/architecture/events.md`
6. `docs/operations/runbook.md`
7. `docs/operations/monitoring.md`

Documentation map:

- Architecture
  - `docs/architecture/overview.md`
  - `docs/architecture/service_catalogue.md`
  - `docs/architecture/data_model.md`
  - `docs/architecture/events.md`
  - `docs/architecture/acceptance_catalogue.md`
  - `docs/architecture/runtime_and_deployment.md`
  - `docs/architecture/testing_strategy.md`
- Operations
  - `docs/operations/runbook.md`
  - `docs/operations/monitoring.md`
- Guides
  - `docs/guides/running_locally.md`
  - `docs/guides/manual_integration_testing.md`
  - `docs/guides/kubernetes_demo.md`
  - `docs/guides/broker_service_implementation.md`
- Delivery records
  - `docs/state/PHASE_1_DONE.md` ... `docs/state/PHASE_9_DONE.md`
  - `docs/state/FINAL_REPORT.md`

Build the docs site:

```powershell
.\.venv\Scripts\python.exe -m mkdocs build --strict
```
