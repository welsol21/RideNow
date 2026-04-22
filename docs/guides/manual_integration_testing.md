# Manual Integration Testing

This guide is the fastest way to manually exercise the full user-facing
RideNow flow after the stack is running.

## Prerequisites

- start the stack with `.\scripts\start.ps1`
- use `Git Bash` or another shell with real `curl`

## Demo Customer IDs

These customer identifiers are intentional scenario switches:

- `customer-demo` -> happy path, should end in `payment-confirmed`
- `customer-no-driver` -> driver failure branch, should end in `no-driver-available`
- `customer-payment-fail` -> payment failure branch, should end in `payment-failed`

## Helper Script

Run the manual helper from Git Bash:

```bash
./scripts/integration_manual_test.sh health
./scripts/integration_manual_test.sh happy
./scripts/integration_manual_test.sh no-driver
./scripts/integration_manual_test.sh payment-fail
./scripts/integration_manual_test.sh issue <ride_id>
./scripts/integration_manual_test.sh all
```

What it does:

- prints the request payload it sends
- prints the raw JSON response
- polls `GET /rides/{ride_id}` until the expected final status
- supports all three main user-visible ride flows plus issue submission

## Raw Requests

### Health

Request:

```bash
curl "http://127.0.0.1:8001/health"
```

Response:

```json
{"service":"broker","status":"ok"}
```

### Create Ride

Happy path request:

```bash
curl -X POST "http://127.0.0.1:8001/rides" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"customer-demo","pickup":{"lat":53.3498,"lon":-6.2603},"dropoff":{"lat":53.3440,"lon":-6.2672}}'
```

Typical initial response:

```json
{
  "ride_id": "ride-5636aec02e9c",
  "status": "request-submitted"
}
```

### Read Ride Status

Request:

```bash
curl "http://127.0.0.1:8001/rides/<ride_id>"
```

Possible customer-visible statuses:

- `request-submitted`
- `driver-assigned`
- `eta-updated`
- `payment-authorised`
- `trip-in-progress`
- `ride-completed`
- `payment-confirmed`
- `no-driver-available`
- `payment-failed`

Typical final happy-path response:

```json
{
  "ride_id": "ride-790dc9b45bc4",
  "status": "payment-confirmed",
  "driver": {
    "driver_id": "driver-1",
    "vehicle_id": "vehicle-1"
  },
  "route": {
    "distance_km": 4.8,
    "pickup_eta_minutes": 3,
    "trip_duration_minutes": 11
  },
  "payment": {
    "authorisation_id": "auth-ride-790dc9b45bc4",
    "capture_id": "cap-ride-790dc9b45bc4",
    "amount": 18.5,
    "currency": "EUR",
    "status": "captured"
  },
  "progress": {
    "phase": "ride-completed",
    "driver_lat": 53.3472,
    "driver_lon": -6.2591
  }
}
```

### Submit Issue

Request:

```bash
curl -X POST "http://127.0.0.1:8001/issues" \
  -H "Content-Type: application/json" \
  -d '{"ride_id":"<ride_id>","customer_id":"customer-demo","category":"payment","description":"Manual integration test follow-up."}'
```

Response:

```json
{
  "issue_id": "issue-6bd60e96c3ce",
  "status": "issue-submitted"
}
```

## Recommended Order

1. `./scripts/integration_manual_test.sh health`
2. `./scripts/integration_manual_test.sh happy`
3. `./scripts/integration_manual_test.sh no-driver`
4. `./scripts/integration_manual_test.sh payment-fail`
5. `./scripts/integration_manual_test.sh issue <ride_id-from-happy-path>`
6. `.\scripts\stop.ps1`
