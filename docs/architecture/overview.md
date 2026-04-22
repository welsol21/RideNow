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

## Current Simplifications and Expansion Points

The repository uses a deliberately regular service skeleton even where a
particular service does not yet need every layer fully populated.

- Several services keep `core/domain/` as a placeholder package with only
  `__init__.py`. This is intentional. Their current behaviour is simple
  enough to live in application use cases, but the domain package is
  already reserved for future entities, value objects, and policy rules.
- Several services also have near-empty `adapters/` packages. Their
  operational integration currently relies on shared RabbitMQ adapters in
  `src/ridenow_shared/adapters/` plus service-local composition in
  `bootstrap/app.py`. If a service later adds a dedicated HTTP surface,
  persistence adapter, external client, or service-specific logging hook,
  that code belongs in its own `adapters/` package.
- This is not a claim that the code is incomplete. It is a statement that
  the system currently implements the minimal runtime complexity required
  by the acceptance catalogue while preserving room for per-service
  growth without structural churn.

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
