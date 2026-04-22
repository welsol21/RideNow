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
