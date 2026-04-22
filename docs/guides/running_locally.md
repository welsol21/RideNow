# Running Locally

This guide gets the full RideNow stack running on a local machine.

## Prerequisites

- Python `3.12+`
- Docker Desktop with Compose

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -e ".[dev,docs,nonfunctional]"
```

## Start the Full Stack

```powershell
.\scripts\start.ps1
```

## Verify Readiness

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/ready"
Invoke-RestMethod "http://127.0.0.1:8002/ready"
Invoke-RestMethod "http://127.0.0.1:8007/ready"
```

## Manual End-to-End Demo

For the quickest manual verification, use the helper script from Git
Bash:

```bash
./scripts/integration_manual_test.sh health
./scripts/integration_manual_test.sh happy
./scripts/integration_manual_test.sh no-driver
./scripts/integration_manual_test.sh payment-fail
```

This script prints:

- the request body it sends
- the immediate API response
- the polled customer-visible ride status until the expected final state

For request/response examples and the `issue` flow, see
`docs/guides/manual_integration_testing.md`.

## Broker CLI

```powershell
.\.venv\Scripts\python.exe -m ridenow_broker.adapters.cli health
.\.venv\Scripts\python.exe -m ridenow_broker.adapters.cli request-ride --customer-id customer-cli --pickup-lat 53.3498 --pickup-lon -6.2603 --dropoff-lat 53.3440 --dropoff-lon -6.2672
.\.venv\Scripts\python.exe -m ridenow_broker.adapters.cli submit-issue --ride-id ride-1 --customer-id customer-cli --category support --description "Demo issue"
```

## Stop the Stack

```powershell
.\scripts\stop.ps1
```
