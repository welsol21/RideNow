# Broker Service Implementation

Broker is the only public business API in the RideNow runtime. It owns
customer-visible state and translates downstream service outcomes into a
single read model.

## Why Broker Exists

- Accept customer ride requests
- Expose current ride status
- Accept customer issue submissions
- Persist the read model that customers observe

Broker does not shortcut the rest of the topology in real runtime mode.
It publishes events and consumes downstream outcomes over RabbitMQ.

## Inbound Adapters

### HTTP

Implemented in `services/broker/src/ridenow_broker/adapters/http.py`.

Routes:

- `GET /health`
- `GET /ready`
- `POST /rides`
- `GET /rides/{ride_id}`
- `POST /issues`

### CLI

Implemented in `services/broker/src/ridenow_broker/adapters/cli.py`.

Commands:

- `health`
- `request-ride`
- `submit-issue`

## Runtime Modes

### Local runtime

Implemented in `services/broker/src/ridenow_broker/bootstrap/runtime.py`.

- Uses in-memory state stores and in-memory event bus
- Recreates the whole service graph inside one process
- Supports fast acceptance tests and CLI tests

### Real runtime

Implemented in `services/broker/src/ridenow_broker/bootstrap/real_runtime.py`.

- Uses PostgreSQL for ride and issue state
- Uses RabbitMQ publisher and consumer adapters
- Subscribes to visible downstream events
- Publishes `RideRequested` and `IssueSubmitted`

## Read Model

Broker maintains customer-visible state keyed by `ride_id`.

Fields evolve as events arrive:

- `driver`
- `route`
- `payment`
- `progress`

The read model is returned directly by `GET /rides/{ride_id}`.

## Event Responsibilities

Broker publishes:

- `RideRequested`
- `IssueSubmitted`

Broker applies:

- `DriverAssigned`
- `EtaUpdated`
- `PaymentAuthorised`
- `TripProgressVisible`
- `RideCompletedVisible`
- `PaymentConfirmedVisible`
- `NoDriverAvailableVisible`
- `PaymentFailedVisible`

## Persistence

Broker is the only service in the current scope with durable business
state. It uses the shared PostgreSQL JSONB adapter and logical stores:

- `broker-ride-status`
- `broker-issue-store`

## Testing

Broker behavior is covered by:

- unit tests for inbound and apply use cases
- acceptance tests for all customer-visible stories
- CLI acceptance tests
- Compose E2E smoke
- non-functional load and resilience checks
