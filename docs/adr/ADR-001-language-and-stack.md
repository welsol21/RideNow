# ADR-001 - Language And Stack

## Status

Accepted

## Context

RideNow requires seven collaborating microservices, an event-driven
backbone, strict outside-in TDD, local container orchestration,
Kubernetes deployment artefacts, and a strong automated testing story.
The stack must favour fast iteration, explicit interfaces, and clear
operability.

## Decisions

### Language and runtime version

- Decision: Python 3.12+
- Justification: Python 3.12 offers strong library support, fast test
  feedback, mature async tooling, and good ergonomics for service-heavy
  delivery under strict TDD.

### Test framework

- Decision: `pytest`
- Justification: `pytest` supports readable acceptance, integration,
  contract, and unit tests with fixtures that suit outside-in delivery.

### Dependency injection approach

- Decision: explicit composition roots per service using plain Python
  factories and wiring modules
- Justification: hand-rolled wiring keeps service boundaries obvious and
  avoids framework magic in the domain and application layers.

### HTTP framework

- Decision: FastAPI
- Justification: FastAPI provides typed request/response boundaries,
  async support, and straightforward health/readiness adapters for
  service-oriented APIs.

### Persistence strategy

- Decision: PostgreSQL for durable service state where persistence is
  required
- Justification: PostgreSQL is stable, well understood, and suitable
  for durable state while keeping services independent at the database
  boundary.

### Event backbone

- Decision: RabbitMQ
- Justification: RabbitMQ supports explicit message-driven collaboration,
  routing patterns, retries, and isolation between services.

### Event serialisation format

- Decision: JSON
- Justification: JSON keeps events readable, debuggable, and simple to
  exchange across independently deployable services.

### Monitoring approach

- Decision: structured logs, `/health`, `/ready`, and Prometheus-style
  metrics
- Justification: this provides a minimal but real operational baseline
  for local demos and containerised deployment.

## Consequences

- The codebase will favour clear module boundaries and explicit ports.
- Each service will own its own composition root.
- Async collaboration will be visible in tests through RabbitMQ-backed
  event flows.
- The system remains relatively lightweight to operate locally while
  still supporting the assignment's observability requirements.
