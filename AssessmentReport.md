# Assessment Report

> Personalisation note:
> The assignment explicitly asks for some sections in your own words and
> not as raw GenAI output. This file is therefore a structured draft for
> your final submission. Before submitting, rewrite the sections marked
> `Personalise` into your own voice and keep only the points you are
> prepared to defend in a follow-up viva.

This report is supported by the running development record in
`docs/input/Development_Log.md`, which I tried to maintain throughout
the project rather than reconstruct only at the end.

## 1. Microservices and GenAI Use

The final RideNow implementation contains these microservices:

| Service      | Final implementation status | Developed fully by hand without GenAI? |
| ------------ | --------------------------- | -------------------------------------- |
| Broker       | Implemented and running     | No                                     |
| Driver       | Implemented and running     | No                                     |
| Route        | Implemented and running     | No                                     |
| Pricing      | Implemented and running     | No                                     |
| Payment      | Implemented and running     | No                                     |
| Tracking     | Implemented and running     | No                                     |
| Notification | Implemented and running     | No                                     |

### Manual contribution and why no final service was kept as hand-written

The strongest manual contribution in this project was not one isolated
service, but the control of the whole development process.

- Roughly one week was spent shaping and correcting the governing prompt
  before the second successful implementation attempt.
- During the first attempt, the generated code collapsed into a
  Broker-centric solution and did not satisfy the required seven-service
  architecture.
- I also discovered that keeping one "manual" service as a special case
  was breaking the consistency of the AI implementation pipeline and
  repeatedly pulled the project away from the assignment scope.
- Because the assignment scope was large and the deadline risk was real,
  I made the pragmatic decision to stop forcing one service to be
  hand-written and instead to use GenAI across the full codebase while
  keeping architecture review, prompt design, debugging direction,
  validation, and corrective decisions under manual control.
- That process was documented continuously in
  `docs/input/Development_Log.md`, so the report is not the only record
  of how the implementation evolved.

### Personalise

Rewrite this section in your own voice before submission. A concise
version you can adapt is:

> I did not end up keeping any one production microservice as fully
> hand-written code. My main non-GenAI contribution was the design and
> control of the development process itself: I spent about a week
> building and correcting the prompt, checking the architecture,
> rejecting a failed Broker-only result, and steering the project back to
> the full seven-service solution. I originally tried to preserve a
> manual service boundary, but that was interfering with the AI workflow
> and increased the risk of missing the deadline, so I chose a consistent
> GenAI-assisted implementation across all services.

## 2. Event-Driven Architecture Employed

RideNow is organised as a set of service nodes connected by RabbitMQ
events. The public API belongs to `broker`, but the business flow is not
implemented as one big synchronous call chain. Instead, services react to
messages, publish new outcomes, and keep the overall system moving in
small steps.

The main happy path is:

1. `broker` accepts `POST /rides` and publishes `RideRequested`
2. `notification` converts that into `DriverSearchRequested`
3. `driver` publishes `DriverAssigned`
4. `notification` asks `route` for ETA
5. `route` publishes `EtaUpdated`
6. `notification` asks `pricing` for fare
7. `pricing` publishes `FareEstimated`
8. `notification` asks `payment` for authorisation
9. `payment` publishes `PaymentAuthorised`
10. `driver` emits location updates
11. `tracking` derives progress and completion events
12. `payment` captures the payment
13. `broker` updates the customer-visible status until
    `payment-confirmed`

### Brief Explanation of the Event-Driven Architecture

The event-driven architecture of RideNow was mainly shaped by three ideas: data-driven microservices, hexagonal architecture, and ROS 2. In particular, ROS 2 influenced how I thought about message passing between services. I liked the idea that the message channel behaves like a peripheral nervous system: an external signal enters the system, the relevant node reacts, and the rest of the platform can respond without everything being tied together through one long direct call chain.

I applied the same principle here with RabbitMQ. Broker is the public entry point for the customer, but the ride flow itself is carried by smaller services that react to events and publish new ones. This reduces coupling between services, keeps responsibilities narrower, and allows the system to respond to new external input through asynchronous event propagation rather than through tightly coupled synchronous calls.

#### Simple diagram

```text
Client
  |
  v
Broker --RideRequested--> Notification --DriverSearchRequested--> Driver
  ^                             |                                   |
  |                             +--> RouteRequested --------------> Route
  |                             +--> FareRequested ---------------> Pricing
  |                             +--> PaymentAuthorisationRequested -> Payment
  |                             +--> TrackingLocationUpdated -----> Tracking
  |<---- visible customer updates and final state via Notification/Payment/Tracking
```

For the full event catalogue, see `docs/architecture/events.md`.

## 3. Tests Implemented and How to Run Them

The project uses several test layers so that failures can be caught at
different distances from the real runtime:

| Layer          | Directory             | Purpose                                                   |
| -------------- | --------------------- | --------------------------------------------------------- |
| Unit           | `tests/unit`          | Small use cases, relays, helpers, and service-local logic |
| Acceptance     | `tests/acceptance`    | Customer-visible Broker scenarios                         |
| Contracts      | `tests/contracts`     | Shared adapter contracts for in-memory and real adapters  |
| Integration    | `tests/integration`   | Service graph, real adapters, and runtime wiring          |
| E2E            | `tests/e2e`           | Live smoke checks against the running stack               |
| Non-functional | `tests/nonfunctional` | Load, resilience, audit, and monitoring checks            |

### Main commands

Run unit tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/unit
```

Run acceptance tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/acceptance
```

Run contract and integration tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/contracts tests/integration
```

Run E2E and non-functional verification:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/e2e tests/nonfunctional
```

Run the full quality gate:

```powershell
.\.venv\Scripts\python.exe -m ruff check src services tests
.\.venv\Scripts\python.exe -m mypy src services tests/nonfunctional
.\.venv\Scripts\python.exe -m pytest -q tests/unit tests/acceptance tests/contracts tests/integration tests/e2e tests/nonfunctional
```

## 4. Monitoring Overview

The monitoring solution is intentionally lightweight but complete enough
for a coursework system:

- every service exposes `/health`, `/ready`, and `/metrics`
- Prometheus scrapes the Compose runtime
- HTTP metrics are exposed in Prometheus format
- services emit structured JSON logs to stdout
- E2E and non-functional tests verify that probes and metrics are alive

Operationally, this means I can:

- check service liveness and readiness
- inspect request rates and request durations
- stream structured logs from containers
- confirm that all seven services are visible to Prometheus

### Personalise

Rewrite this section briefly in your own words. A good short version is:

> I used a simple monitoring setup based on health probes, readiness
> probes, JSON logs, and Prometheus metrics. This was enough to observe
> whether each service was alive, whether the stack was ready to accept
> traffic, and whether requests were actually moving through the runtime.
> I did not try to build a full production observability platform, but I
> did implement the essential monitoring hooks that make a distributed
> system inspectable.

## 5. Video Reflection Preparation

The assignment also asks for a short reflection video. A ready-made
recording outline is provided in `VideoScript.md`.

The most important points to cover are:

- where GenAI helped most
- where GenAI failed or misled the project
- what had to be fixed manually
- how the final system works live in Kubernetes
- what you now understand that GenAI cannot replace

## 6. Kubernetes Demo Commands

Yes, this part is implemented and can be shown live.

At the time of writing, the local Kubernetes context is:

```powershell
kubectl config current-context
```

Example runtime inspection command:

```powershell
kubectl -n ridenow get pods,svc
```

Useful live demo sequence:

```powershell
kubectl -n ridenow get pods,svc
kubectl -n ridenow port-forward svc/broker 8001:8001
```

In a second terminal:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/health"
Invoke-RestMethod "http://127.0.0.1:8001/ready"
```

Then create a ride and poll:

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
Invoke-RestMethod "http://127.0.0.1:8001/rides/$($response.ride_id)"
```

You can also stream service logs during the demo:

```powershell
kubectl -n ridenow logs deploy/broker -f
kubectl -n ridenow logs deploy/notification -f
kubectl -n ridenow logs deploy/payment -f
```
