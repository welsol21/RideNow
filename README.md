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
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8001/ready
```

Submit a ride:

```powershell
curl -X POST http://127.0.0.1:8001/rides ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_id\":\"customer-demo\",\"pickup\":{\"lat\":53.3498,\"lon\":-6.2603},\"dropoff\":{\"lat\":53.3440,\"lon\":-6.2672}}"
```

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

- Architecture: `docs/architecture/`
- Operations: `docs/operations/`
- Guides: `docs/guides/`
- Build docs site:

```powershell
.\.venv\Scripts\python.exe -m mkdocs build --strict
```
