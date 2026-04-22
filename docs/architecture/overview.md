# Architecture Overview

RideNow is implemented as seven collaborating services connected through
an event-driven backbone.

## Services

- `broker`: public HTTP API, customer-visible read model, issue capture
- `notification`: relay and visibility boundary between services
- `driver`: deterministic driver assignment and driver location emission
- `route`: deterministic route and ETA calculation
- `pricing`: deterministic fare estimation
- `payment`: payment authorisation and capture
- `tracking`: trip progress and trip completion

## System Shape

1. A customer sends `POST /rides` to `broker`.
2. `broker` stores the initial request status and emits `RideRequested`.
3. `notification` fans the request into the downstream workflow.
4. Domain services publish outcomes back onto RabbitMQ.
5. `notification` emits Broker-visible events where needed.
6. `broker` updates the customer-facing read model consumed by `GET /rides/{ride_id}`.

## Architectural Style

- Per-service composition root in `services/<name>/src/.../bootstrap/app.py`
- Shared infrastructure code in `src/ridenow_shared/`
- Event contracts based on `EventEnvelope` and `DomainEventPayload`
- FastAPI probe app for every service
- RabbitMQ topic exchange for inter-service communication
- PostgreSQL JSONB state store for persistent Broker state

## Public Surface

Only `broker` exposes customer-facing business endpoints:

- `POST /rides`
- `GET /rides/{ride_id}`
- `POST /issues`

Every service exposes operational endpoints:

- `GET /health`
- `GET /ready`
- `GET /metrics`

## Delivery Approach

The implementation followed top-down outside-in TDD:

1. Full-system integration baseline
2. Contract tests for outbound ports
3. User stories through acceptance tests
4. Real adapter wiring
5. E2E, observability, and non-functional gates
