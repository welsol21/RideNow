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
curl http://127.0.0.1:8001/ready
curl http://127.0.0.1:8002/ready
curl http://127.0.0.1:8007/ready
```

## Happy-Path Demo

Create a ride:

```powershell
curl -X POST http://127.0.0.1:8001/rides ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_id\":\"customer-demo\",\"pickup\":{\"lat\":53.3498,\"lon\":-6.2603},\"dropoff\":{\"lat\":53.3440,\"lon\":-6.2672}}"
```

Poll the ride:

```powershell
curl http://127.0.0.1:8001/rides/<ride-id>
```

The ride should progress to:

- `request-submitted`
- `driver-assigned`
- `eta-updated`
- `payment-authorised`
- `trip-in-progress`
- `ride-completed`
- `payment-confirmed`

## Failure Demos

No driver available:

```powershell
curl -X POST http://127.0.0.1:8001/rides ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_id\":\"customer-no-driver\",\"pickup\":{\"lat\":53.3498,\"lon\":-6.2603},\"dropoff\":{\"lat\":53.3440,\"lon\":-6.2672}}"
```

Payment failed:

```powershell
curl -X POST http://127.0.0.1:8001/rides ^
  -H "Content-Type: application/json" ^
  -d "{\"customer_id\":\"customer-payment-fail\",\"pickup\":{\"lat\":53.3498,\"lon\":-6.2603},\"dropoff\":{\"lat\":53.3440,\"lon\":-6.2672}}"
```

## Submit an Issue

```powershell
curl -X POST http://127.0.0.1:8001/issues ^
  -H "Content-Type: application/json" ^
  -d "{\"ride_id\":\"<ride-id>\",\"customer_id\":\"customer-demo\",\"category\":\"payment\",\"description\":\"Need a refund check.\"}"
```

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
