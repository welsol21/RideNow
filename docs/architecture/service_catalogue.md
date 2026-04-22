# Service Catalogue

This document identifies the implementation scope of each microservice.

## Summary

| Service | Primary responsibility | Inbound surface | Outbound surface | Persistent state |
| --- | --- | --- | --- | --- |
| Broker | Public API and customer-visible ride state | HTTP, CLI | RabbitMQ publish/consume, PostgreSQL state store | Yes |
| Driver | Driver assignment and location emission | RabbitMQ consume | RabbitMQ publish | No |
| Route | Route and ETA calculation | RabbitMQ consume | RabbitMQ publish | No |
| Pricing | Fare estimation | RabbitMQ consume | RabbitMQ publish | No |
| Payment | Payment authorisation and capture | RabbitMQ consume | RabbitMQ publish | No |
| Tracking | Trip progress and trip completion | RabbitMQ consume | RabbitMQ publish | No |
| Notification | Relay, fan-out, and visible-event projection | RabbitMQ consume | RabbitMQ publish | No |

## Structural Notes

- Every service keeps the same high-level package shape:
  `adapters/`, `bootstrap/`, `core/application/`, `core/domain/`.
- In the current implementation, `broker` is the only service with a
  substantial service-local inbound adapter surface because it owns the
  public API and CLI.
- The other services are intentionally lighter:
  - their transport wiring is mostly assembled in `bootstrap/app.py`
  - their RabbitMQ integration uses shared code from
    `src/ridenow_shared/adapters/`
  - several `core/domain/` and `adapters/` packages are placeholders for
    future complexity rather than current omissions
- This keeps the current demo/runtime small without blocking later
  extraction of service-specific adapters, persistence, or richer domain
  models.

## Broker

- Implements:
  - `POST /rides`
  - `GET /rides/{ride_id}`
  - `POST /issues`
  - `GET /health`, `GET /ready`, `GET /metrics`
  - CLI commands `health`, `request-ride`, `submit-issue`
- Owns:
  - customer-visible ride lifecycle
  - issue acknowledgement
  - PostgreSQL stores `broker-ride-status` and `broker-issue-store`
- Consumes:
  - `DriverAssigned`
  - `EtaUpdated`
  - `PaymentAuthorised`
  - `TripProgressVisible`
  - `RideCompletedVisible`
  - `PaymentConfirmedVisible`
  - `NoDriverAvailableVisible`
  - `PaymentFailedVisible`
- Publishes:
  - `RideRequested`
  - `IssueSubmitted`

## Driver

- Implements:
  - driver assignment decision
  - deterministic no-driver branch
  - driver location emission after payment authorisation
- Current scaling note:
  - no service-local inbound HTTP adapter or datastore is needed yet
  - if driver search becomes non-trivial, `core/domain/` is the intended
    home for driver availability rules, matching policies, and geographic
    constraints
- Consumes:
  - `DriverSearchRequested`
  - `PaymentAuthorised`
- Publishes:
  - `DriverAssigned`
  - `NoDriverAvailable`
  - `DriverLocationUpdated`

## Route

- Implements deterministic route calculation for the demo workflow
- Consumes:
  - `RouteRequested`
- Publishes:
  - `EtaUpdated`
- Current scaling note:
  - route logic is still simple enough to remain in application code
  - a richer version could move route models, map abstractions, and ETA
    policies into `core/domain/` and provider-specific clients into
    `adapters/`

## Pricing

- Implements deterministic fare calculation for the demo workflow
- Consumes:
  - `FareRequested`
- Publishes:
  - `FareEstimated`
- Current scaling note:
  - pricing is intentionally deterministic for repeatable tests
  - surge rules, promotions, tax handling, and pricing engines would be
    natural future residents of `core/domain/` and service-local
    adapters

## Payment

- Implements payment authorisation and capture
- Supports deterministic failure for `customer-payment-fail`
- Consumes:
  - `PaymentAuthorisationRequested`
  - `PaymentCaptureRequested`
- Publishes:
  - `PaymentAuthorised`
  - `PaymentFailed`
  - `PaymentCaptured`
- Current scaling note:
  - payment transport is RabbitMQ-only in the current scope
  - third-party PSP clients, retries, idempotency stores, and ledger
    persistence would fit naturally into `adapters/` plus a richer domain
    layer

## Tracking

- Implements trip progress and trip completion
- Consumes:
  - `TrackingLocationUpdated`
- Publishes:
  - `TripStatusUpdated`
  - `TripCompleted`
- Current scaling note:
  - tracking is currently stateless beyond emitted events
  - route snapshots, geofencing, and historical trip progression would
    likely introduce service-owned persistence and more substantial
    domain models

## Notification

- Implements the relay layer between services and Broker-visible events
- Consumes:
  - `RideRequested`
  - `NoDriverAvailable`
  - `DriverAssigned`
  - `EtaUpdated`
  - `FareEstimated`
  - `PaymentFailed`
  - `DriverLocationUpdated`
  - `TripStatusUpdated`
  - `TripCompleted`
  - `PaymentCaptured`
- Publishes:
  - `DriverSearchRequested`
  - `NoDriverAvailableVisible`
  - `RouteRequested`
  - `FareRequested`
  - `PaymentAuthorisationRequested`
  - `PaymentFailedVisible`
  - `TrackingLocationUpdated`
  - `TripProgressVisible`
  - `RideCompletedVisible`
  - `PaymentCaptureRequested`
  - `PaymentConfirmedVisible`
- Current scaling note:
  - Notification is a relay/projection service in the current scope
  - if delivery guarantees, template rendering, channel fan-out, or
    audit history were required, it would grow its own adapters and
    persistence rather than staying a thin event router
