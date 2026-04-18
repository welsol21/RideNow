# Reference Analysis - RideNow

## Purpose

This document captures the concrete analysis baseline for the second
implementation attempt of `ridenow`. It translates the approved
architecture into bounded responsibilities, user stories, events,
operating modes, and constraints that will drive the acceptance-first
implementation plan.

## Service Catalogue And Responsibilities

### Broker Service

- Customer-facing coordination boundary.
- Accepts customer requests and returns immediate acknowledgements.
- Tracks the customer-visible ride lifecycle.
- Translates internal outcomes into customer-facing states.
- Accepts issue and complaint submissions.

### Driver Service

- Owns driver and vehicle availability.
- Selects eligible drivers for ride requests.
- Publishes driver assignment and live driver-location updates.
- Maintains driver operational state such as online/offline and busy/free.

### Route Service

- Computes driver-to-pickup and pickup-to-dropoff routes.
- Calculates ETA and distance.
- Handles route recalculation when tracking signals deviation or delay.

### Pricing Service

- Calculates fare estimates and final ride fare.
- Applies pricing rules and surge logic using route and distance inputs.

### Payment Service

- Authorises, captures, and refunds payments.
- Emits payment-authorised, payment-failed, payment-confirmed, and refund outcomes.

### Tracking Service

- Interprets location-derived ride progress.
- Detects driver-arriving, trip-started, in-progress, and trip-completed states.
- Detects route deviation conditions that require rerouting.

### Notification Service

- Provides cross-service event dissemination over the event backbone.
- Routes relevant events to interested services and back to Broker.
- Maintains delivery and retry concerns outside service domain cores.

## Entities And Value Objects

### Core entities

- `Ride`
- `RideStatusView`
- `Driver`
- `Vehicle`
- `RoutePlan`
- `FareQuote`
- `PaymentTransaction`
- `TripProgress`
- `Issue`
- `NotificationEnvelope`

### Representative value objects

- `RideId`
- `CustomerId`
- `DriverId`
- `IssueId`
- `Money`
- `Currency`
- `Coordinate`
- `LocationTimestamp`
- `EtaMinutes`
- `DistanceKm`
- `CorrelationId`
- `EventId`
- `RetryCount`

## User Stories

These are the minimum user stories and their dependency order.

1. As a passenger, I can request a ride, so that the system acknowledges my request immediately.
2. As a passenger, I can receive a driver assignment, so that I know a ride is being arranged.
3. As a passenger, I can receive ETA and route-related feedback, so that I know when the driver will arrive and how long the trip will take.
4. As a passenger, I can have payment authorised, so that the ride can proceed.
5. As a passenger, I can see trip progress, so that I know whether the driver is arriving or the trip is in progress.
6. As a passenger, I can complete a ride and receive payment confirmation, so that the journey closes correctly.
7. As a passenger, I can experience a no-driver-available outcome, so that I receive clear failure feedback.
8. As a passenger, I can experience a payment-failed outcome, so that I receive clear failure feedback.
9. As a passenger, I can submit an issue/complaint, so that the system acknowledges and routes it appropriately.

## Main Operating Modes

The project must prove the full service graph in these modes before
deep service-local implementation continues.

- `request-ride-acknowledgement`
- `driver-assigned`
- `route-and-eta-feedback`
- `payment-authorised`
- `trip-progress`
- `ride-completed-payment-confirmed`
- `no-driver-available`
- `payment-failed`
- `issue-submitted`
- `stack-startup-readiness`
- `stack-shutdown`
- `manual-demo-mode`

## Inbound And Outbound Interactions

### Customer-facing inbound interactions

- `POST /rides`
- `GET /rides/{ride_id}`
- `POST /issues`
- Health and readiness probes

### System-level inbound interactions

- Event subscriptions through RabbitMQ for service collaboration.
- Internal service health and readiness probes.
- Local demo bootstrap and shutdown commands.

### Outbound interactions

- Event publication to RabbitMQ.
- Persistence to PostgreSQL where durable state is required.
- Structured logs and metrics emission.

## Customer-Visible Lifecycle

- Request submitted
- Waiting for driver
- Driver assigned
- Driver arriving
- Payment authorised
- Ride in progress
- Ride completed
- Payment confirmed
- No driver available
- Payment failed
- Issue submitted
- Issue under review
- Refunded or resolved

## Business Rules And Invariants

- A passenger request must be acknowledged immediately by Broker even if the final business outcome arrives later.
- A ride must have a stable `ride_id` and correlation identifier across all collaborating services.
- Customer-visible state changes must be derived from immutable events.
- Driver assignment cannot occur without an outstanding ride request.
- Route and ETA feedback require both a ride context and a driver context.
- Payment authorisation is required before ride execution enters the ride-in-progress path.
- Trip completion cannot be declared before trip progress has reached an active ride state.
- Failure paths such as no-driver-available and payment-failed must be customer-visible terminal states unless an explicit recovery flow exists.
- Issue submission must be acknowledged immediately and must produce a traceable issue identifier.
- Services may not depend on hidden direct cross-service imports; collaboration must occur through ports, events, or documented APIs.

## Edge Cases

- Duplicate ride-request submissions with the same client correlation key.
- Driver becomes unavailable after assignment but before pickup.
- Route recalculation required due to traffic or tracked deviation.
- Payment authorisation timeout or partial downstream outage.
- Out-of-order location updates.
- Duplicate or retried events on the message backbone.
- Service restart during an in-flight ride.
- Issue submitted for a ride already in terminal failure state.

## Event Catalogue

- `RideRequested`
- `RideAcknowledged`
- `DriverSearchRequested`
- `DriverAssigned`
- `NoDriverAvailable`
- `RouteRequested`
- `RouteCalculated`
- `EtaUpdated`
- `FareEstimated`
- `PaymentAuthorisationRequested`
- `PaymentAuthorised`
- `PaymentFailed`
- `DriverLocationUpdated`
- `DriverArriving`
- `TripStarted`
- `TripProgressUpdated`
- `TripCompleted`
- `PaymentCaptured`
- `PaymentConfirmed`
- `IssueSubmitted`
- `IssueRouted`
- `IssueResolved`
- `RefundIssued`

## Routing Problem Statement

The Route Service must solve:

- `D -> P`
- `P -> Q`
- `D -> P -> Q`

Where:

- `D` is the driver location,
- `P` is the pickup point,
- `Q` is the dropoff point.

The service must return the selected route, ETA, distance, and enough
metadata for Pricing and Broker to produce customer-visible feedback.

## Timing And Configuration Rules

- Acknowledge customer actions immediately and complete downstream work asynchronously.
- Externalise all timeouts, retry limits, polling intervals, and thresholds into configuration.
- Use service-local configuration for:
  - driver availability windows;
  - ETA refresh interval;
  - reroute thresholds;
  - payment timeouts and retries;
  - notification retry/backoff policy;
  - tracking stale-location detection.

## GenAI Implementation Scope Across Services

This second attempt treats all seven services as AI-generated
production services. No required service is reserved as a manual-only
implementation boundary.

The work must still satisfy:

- full architecture completeness,
- real inter-service collaboration,
- one-command local start,
- one-command local stop,
- demo-ready state with dummy/demo data,
- full-system integration-first implementation discipline.
