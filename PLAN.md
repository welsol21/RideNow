# Project Plan - ridenow

## Legend

- [ ] pending · [x] done
- ACC-RED = write failing acceptance or integration test
- UNIT-RED = write failing unit test for next missing piece
- UNIT-GREEN = minimum code to pass
- ACC-GREEN = acceptance or integration test now passes
- REFACTOR = clean up, all tests stay green

## Current Pointer

- Next unchecked item: `2.1`

## Phase 0 - Bootstrap

- [x] 0.1 Read project context
- [x] 0.2 Write docs/analysis/reference_analysis.md
- [x] 0.3 Write PLAN.md
- [x] 0.4 Write docs/adr/ADR-001-language-and-stack.md
- [x] 0.5 Commit bootstrap

## Phase 1 - Skeleton

- [x] 1.1 Create directory tree
- [x] 1.2 Create dependency manifest with pinned versions
- [x] 1.3 Create strict lint/format/type configs
- [x] 1.4 Create CI pipeline
- [x] 1.5 Create .gitignore, .editorconfig, base README
- [x] 1.6 Create shared events/contracts/config package
- [x] 1.7 Create Dockerfiles and base docker-compose
- [x] 1.8 PHASE 1 GATE: lint + build
- [x] 1.9 Write docs/state/PHASE_1_DONE.md

## Phase 2 - Walking Skeleton

- [ ] 2.1 ACC-RED - acceptance test "health check returns ok"
- [ ] 2.2 UNIT-GREEN - define HealthCheck port + trivial use case
- [ ] 2.3 UNIT-GREEN - implement minimal HTTP adapter
- [ ] 2.4 UNIT-GREEN - implement minimal outbound stub adapter
- [ ] 2.5 UNIT-GREEN - wire composition root
- [ ] 2.6 ACC-GREEN - walking skeleton passes
- [ ] 2.7 REFACTOR
- [ ] 2.8 PHASE 2 GATE
- [ ] 2.9 Write docs/state/PHASE_2_DONE.md

## Phase 2A - Full-System Integration Baseline

- [ ] 2A.1 ACC-RED - full-system startup and readiness integration matrix
- [ ] 2A.2 ACC-RED - happy-path service-connectivity integration slice
- [ ] 2A.3 ACC-RED - failure-path service-connectivity integration slice
- [ ] 2A.4 ACC-RED - manual-demo-mode integration slice
- [ ] 2A.5 UNIT-GREEN - minimum topology wiring to make the first full-system integration test pass
- [ ] 2A.6 REFACTOR
- [ ] 2A.7 PHASE 2A GATE - named operating-mode connectivity established
- [ ] 2A.8 Write docs/state/PHASE_2A_DONE.md

## Phase 3 - Port Contracts & In-Memory Adapters

- [ ] 3.1 Define outbound ports for generated services
- [ ] 3.2 UNIT-RED - shared contract suite per port
- [ ] 3.3 UNIT-GREEN - in-memory adapters per port
- [ ] 3.4 REFACTOR
- [ ] 3.5 PHASE 3 GATE
- [ ] 3.6 Write docs/state/PHASE_3_DONE.md

## Phase 4 - User Stories (outside-in, one at a time)

### 4.1 Story: request-ride-acknowledgement
- [ ] 4.1.0 Write docs/state/STORY_request-ride-acknowledgement_START.md
- [ ] 4.1.1 ACC-RED
- [ ] 4.1.2 Confirm failure reason
- [ ] 4.1.3 UNIT-RED
- [ ] 4.1.4 UNIT-GREEN
- [ ] 4.1.5 UNIT-REFACTOR
- [ ] 4.1.6 Repeat inward TDD until acceptance is green
- [ ] 4.1.7 ACC-GREEN
- [ ] 4.1.8 Run all prior acceptance tests
- [ ] 4.1.9 ACC-REFACTOR
- [ ] 4.1.10 Write docs/state/STORY_request-ride-acknowledgement_DONE.md

### 4.2 Story: driver-assigned
- [ ] 4.2.0 Write docs/state/STORY_driver-assigned_START.md
- [ ] 4.2.1 ACC-RED
- [ ] 4.2.2 Confirm failure reason
- [ ] 4.2.3 UNIT-RED
- [ ] 4.2.4 UNIT-GREEN
- [ ] 4.2.5 UNIT-REFACTOR
- [ ] 4.2.6 Repeat inward TDD until acceptance is green
- [ ] 4.2.7 ACC-GREEN
- [ ] 4.2.8 Run all prior acceptance tests
- [ ] 4.2.9 ACC-REFACTOR
- [ ] 4.2.10 Write docs/state/STORY_driver-assigned_DONE.md

### 4.3 Story: route-and-eta-feedback
- [ ] 4.3.0 Write docs/state/STORY_route-and-eta-feedback_START.md
- [ ] 4.3.1 ACC-RED
- [ ] 4.3.2 Confirm failure reason
- [ ] 4.3.3 UNIT-RED
- [ ] 4.3.4 UNIT-GREEN
- [ ] 4.3.5 UNIT-REFACTOR
- [ ] 4.3.6 Repeat inward TDD until acceptance is green
- [ ] 4.3.7 ACC-GREEN
- [ ] 4.3.8 Run all prior acceptance tests
- [ ] 4.3.9 ACC-REFACTOR
- [ ] 4.3.10 Write docs/state/STORY_route-and-eta-feedback_DONE.md

### 4.4 Story: payment-authorised
- [ ] 4.4.0 Write docs/state/STORY_payment-authorised_START.md
- [ ] 4.4.1 ACC-RED
- [ ] 4.4.2 Confirm failure reason
- [ ] 4.4.3 UNIT-RED
- [ ] 4.4.4 UNIT-GREEN
- [ ] 4.4.5 UNIT-REFACTOR
- [ ] 4.4.6 Repeat inward TDD until acceptance is green
- [ ] 4.4.7 ACC-GREEN
- [ ] 4.4.8 Run all prior acceptance tests
- [ ] 4.4.9 ACC-REFACTOR
- [ ] 4.4.10 Write docs/state/STORY_payment-authorised_DONE.md

### 4.5 Story: trip-progress
- [ ] 4.5.0 Write docs/state/STORY_trip-progress_START.md
- [ ] 4.5.1 ACC-RED
- [ ] 4.5.2 Confirm failure reason
- [ ] 4.5.3 UNIT-RED
- [ ] 4.5.4 UNIT-GREEN
- [ ] 4.5.5 UNIT-REFACTOR
- [ ] 4.5.6 Repeat inward TDD until acceptance is green
- [ ] 4.5.7 ACC-GREEN
- [ ] 4.5.8 Run all prior acceptance tests
- [ ] 4.5.9 ACC-REFACTOR
- [ ] 4.5.10 Write docs/state/STORY_trip-progress_DONE.md

### 4.6 Story: ride-completed-payment-confirmed
- [ ] 4.6.0 Write docs/state/STORY_ride-completed-payment-confirmed_START.md
- [ ] 4.6.1 ACC-RED
- [ ] 4.6.2 Confirm failure reason
- [ ] 4.6.3 UNIT-RED
- [ ] 4.6.4 UNIT-GREEN
- [ ] 4.6.5 UNIT-REFACTOR
- [ ] 4.6.6 Repeat inward TDD until acceptance is green
- [ ] 4.6.7 ACC-GREEN
- [ ] 4.6.8 Run all prior acceptance tests
- [ ] 4.6.9 ACC-REFACTOR
- [ ] 4.6.10 Write docs/state/STORY_ride-completed-payment-confirmed_DONE.md

### 4.7 Story: no-driver-available
- [ ] 4.7.0 Write docs/state/STORY_no-driver-available_START.md
- [ ] 4.7.1 ACC-RED
- [ ] 4.7.2 Confirm failure reason
- [ ] 4.7.3 UNIT-RED
- [ ] 4.7.4 UNIT-GREEN
- [ ] 4.7.5 UNIT-REFACTOR
- [ ] 4.7.6 Repeat inward TDD until acceptance is green
- [ ] 4.7.7 ACC-GREEN
- [ ] 4.7.8 Run all prior acceptance tests
- [ ] 4.7.9 ACC-REFACTOR
- [ ] 4.7.10 Write docs/state/STORY_no-driver-available_DONE.md

### 4.8 Story: payment-failed
- [ ] 4.8.0 Write docs/state/STORY_payment-failed_START.md
- [ ] 4.8.1 ACC-RED
- [ ] 4.8.2 Confirm failure reason
- [ ] 4.8.3 UNIT-RED
- [ ] 4.8.4 UNIT-GREEN
- [ ] 4.8.5 UNIT-REFACTOR
- [ ] 4.8.6 Repeat inward TDD until acceptance is green
- [ ] 4.8.7 ACC-GREEN
- [ ] 4.8.8 Run all prior acceptance tests
- [ ] 4.8.9 ACC-REFACTOR
- [ ] 4.8.10 Write docs/state/STORY_payment-failed_DONE.md

### 4.9 Story: issue-submitted
- [ ] 4.9.0 Write docs/state/STORY_issue-submitted_START.md
- [ ] 4.9.1 ACC-RED
- [ ] 4.9.2 Confirm failure reason
- [ ] 4.9.3 UNIT-RED
- [ ] 4.9.4 UNIT-GREEN
- [ ] 4.9.5 UNIT-REFACTOR
- [ ] 4.9.6 Repeat inward TDD until acceptance is green
- [ ] 4.9.7 ACC-GREEN
- [ ] 4.9.8 Run all prior acceptance tests
- [ ] 4.9.9 ACC-REFACTOR
- [ ] 4.9.10 Write docs/state/STORY_issue-submitted_DONE.md

- [ ] 4.FINAL.1 All acceptance tests green
- [ ] 4.FINAL.2 Coverage on core ≥ target
- [ ] 4.FINAL.3 Write docs/state/PHASE_4_DONE.md

## Phase 5 - Inbound Adapter Diversity

- [ ] 5.1 ACC-RED - representative acceptance subset through CLI or alternative inbound adapter
- [ ] 5.2 UNIT-GREEN - implement second inbound adapter
- [ ] 5.3 ACC-GREEN
- [ ] 5.4 Write docs/state/PHASE_5_DONE.md

## Phase 6 - Real Outbound Adapters

- [ ] 6.1 Real RabbitMQ adapters + contract/integration tests
- [ ] 6.2 Real PostgreSQL adapters + contract/integration tests
- [ ] 6.3 Real service wiring with Docker Compose
- [ ] 6.4 Kubernetes manifests
- [ ] 6.5 Run full acceptance suite with real adapters wired
- [ ] 6.6 PHASE 6 GATE
- [ ] 6.7 Write docs/state/PHASE_6_DONE.md

## Phase 7 - Smoke E2E & Observability

- [ ] 7.1 E2E smoke tests
- [ ] 7.2 Structured logging
- [ ] 7.3 Metrics endpoint / minimal monitoring
- [ ] 7.4 Health and readiness endpoints
- [ ] 7.5 Full test:e2e + coverage + lint gate
- [ ] 7.6 Write docs/state/PHASE_7_DONE.md

## Phase 8 - Non-Functional and Monitoring Gate

- [ ] 8.1 Performance/load tests
- [ ] 8.2 Resilience/recovery tests
- [ ] 8.3 Security/dependency audit
- [ ] 8.4 Soak/reliability scaffolding
- [ ] 8.5 Monitoring validation
- [ ] 8.6 Write docs/state/PHASE_8_DONE.md

## Phase 9 - Documentation

- [ ] 9.1 README.md
- [ ] 9.2 docs/architecture/overview.md
- [ ] 9.3 docs/architecture/service_catalogue.md
- [ ] 9.4 docs/architecture/data_model.md
- [ ] 9.5 docs/architecture/events.md
- [ ] 9.6 docs/architecture/acceptance_catalogue.md
- [ ] 9.7 docs/architecture/runtime_and_deployment.md
- [ ] 9.8 docs/architecture/testing_strategy.md
- [ ] 9.9 docs/operations/runbook.md
- [ ] 9.10 docs/operations/monitoring.md
- [ ] 9.11 docs/guides/running_locally.md
- [ ] 9.12 docs/guides/kubernetes_demo.md
- [ ] 9.13 docs/guides/broker_service_implementation.md
- [ ] 9.14 Docs list required by the assignment:
      - list of microservices and identify the implementation scope of each
      - event-driven architecture overview
      - tests implemented and how to run them
      - monitoring overview
- [ ] 9.15 Verify docs:build/check succeeds
- [ ] 9.16 Write docs/state/PHASE_9_DONE.md

## Phase 10 - Turnkey Verification

- [ ] 10.1 Fresh-clone test
- [ ] 10.2 Install → test → run with zero manual steps
- [ ] 10.3 Validate compose workflow
- [ ] 10.4 Validate Kubernetes manifests
- [ ] 10.5 Write docs/state/FINAL_REPORT.md

## Backlog

- (append as discovered)
