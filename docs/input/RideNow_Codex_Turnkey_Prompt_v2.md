# TURNKEY PROMPT — RideNow Assessment 2 Implementation

## Turnkey Hexagonal + Data-Driven Microsystem

## Outside-In TDD · Acceptance-First · Full Documentation

You are a principal software engineer. You will deliver a **turnkey**, **production-ready**, **immediately runnable** project based on the approved RideNow architecture and the assignment requirements for **SOFT8026 Assessment 2**. The new project is called **ridenow**.

You will operate **autonomously and silently** — no clarifying
questions, no progress chatter, no pauses for approval. You only
report when a PHASE GATE passes or when a HARD STOP condition triggers
(defined in §4).

**Language choice:** Python 3.12+.
Document and justify the choice in
`docs/adr/ADR-001-language-and-stack.md` during STEP 0.4 and never revisit it.

**Forbidden technologies:** no shared database as a primary service-integration mechanism, no hidden cross-service imports, no hard-coded operational constants in domain logic, no fake monitoring, no placeholder implementations in delivered code.

---

## 1 · TESTING PHILOSOPHY — OUTSIDE-IN TDD (read before anything else)

This is the most important section. Get it wrong and the project
loses consistency; get it right and every commit keeps the whole
system green and provably correct.

### 1.1 Core principle

You test **outside-in**, not bottom-up. For every user story:

1. Write a failing **acceptance test** (scenario/integration test)
   that exercises the full stack through an inbound port and verifies
   the outcome through an outbound port. Red because nothing exists.
2. Work **inward** from that red acceptance test. Write only the
   minimum unit tests and production code needed to turn it green.
   Do not pre-write exhaustive unit tests for classes the acceptance
   test does not yet need.
3. Once acceptance is green, refactor with safety.
4. Next story → next acceptance test. Every prior acceptance test
   must remain green throughout.

### 1.2 Test pyramid you will produce

- **Acceptance tests** — one per user story, written FIRST, exercising
  the real composition of the system with in-memory adapters. Living
  specification. Stay green forever once written.
  Under `tests/acceptance/`.
- **Unit tests** — added on demand, inside-out from each red
  acceptance test. Cover value objects, entity invariants, edge cases,
  and pure logic that the acceptance test cannot easily probe.
  Under `tests/unit/`.
- **Adapter contract tests** — one shared suite per port, executed
  against every adapter implementing that port. Guarantee adapter
  swappability. Under `tests/contracts/`.
- **E2E smoke tests** — minimal set starting the real entry point,
  at least one endpoint per major story. Under `tests/e2e/`.
- **Non-functional tests** — performance, resilience, security, and
  soak/reliability checks required by the assignment. Under
  `tests/nonfunctional/`.

### 1.3 Consistency invariant

At every commit, on every branch, **all acceptance tests pass**.
A commit that red-lights any previously-green acceptance test is
forbidden — fix forward within the same task or revert.

### 1.4 Granularity of the TDD cycle

For each user story:

```text
ACCEPTANCE-RED      → write scenario test, watch it fail
  UNIT-RED          → narrowest unit test for first missing piece
  UNIT-GREEN        → minimum code to pass that unit test
  UNIT-REFACTOR     → optional
  (repeat UNIT-RED/GREEN/REFACTOR until acceptance turns green)
ACCEPTANCE-GREEN    → entire scenario passes
ACCEPTANCE-REFACTOR → tidy up, keep everything green
```

Each phase = separate commit = separate `PLAN.md` checkbox.
Never jump ahead.

### 1.5 What you do NOT do

- Do **not** pre-generate a full unit-test catalogue for every class
  before any scenario runs.
- Do **not** write an acceptance test for a story whose prior
  story's acceptance test is not green yet.
- Do **not** refactor across story boundaries without all affected
  acceptance tests green.

---

## 2 · CONTEXT-LOSS PROTOCOL (read this section twice)

Long agentic runs lose context. The plan lives on **disk**, not
in your context window.

1. Maintain `PLAN.md` at the repo root — the single source of truth.
   Every TODO item is a checkbox.
2. **Before starting any task**, read `PLAN.md` and find the first
   unchecked `[ ]`. That is your next task. Nothing else.
3. **After finishing any task**, update `PLAN.md`: `[ ]` → `[x]`,
   append commit SHA.
4. **After every PHASE GATE passes**, write
   `docs/state/PHASE_{N}_DONE.md`:
   - Summary (≤ 10 bullets)
   - Public API surface added (signatures only)
   - Design decisions made mid-phase
   - Test counts and coverage numbers
   - **List of acceptance tests currently green**
5. **Before starting each new user story in Phase 4+**, write
   `docs/state/STORY_{slug}_START.md`:
   - Exact acceptance-test scenario you will write
   - Which ports it touches
   - Which existing unit tests are expected to stay green
6. **After finishing each user story**, write
   `docs/state/STORY_{slug}_DONE.md`:
   - Acceptance test name and location
   - New units/adapters introduced
   - Confirmation that all prior acceptance tests still pass
7. **Commit after every TODO item.** Message format:
   `phase-{N}/task-{N.N}: <imperative summary>`
8. **Never edit files outside the current task's scope.** Drive-by
   findings go to the Backlog section of `PLAN.md`.

If context is lost: stop, read `PLAN.md`, read every
`PHASE_*_DONE.md` and every `STORY_*_DONE.md` in order, resume at
the first unchecked item. Do not ask. Do not guess.

---

## 3 · NON-NEGOTIABLE STANDARDS

**Architecture.** Hexagonal (Ports & Adapters). Domain layer has zero
infrastructure imports. Every cross-layer call goes through a port.

**Data-driven.** All state changes emit immutable domain events.
All business configuration lives in external config files, never
hard-coded.

**Outside-in TDD.** As defined in §1. No production code without
a failing test that requires it. No unit test without a failing
acceptance test upstream that needs it.

**Docstrings.** Every public module, class, function, method, port,
adapter, command, query, and event has a docstring containing:
purpose · parameters · return value · exceptions raised · one usage
example.

**Coverage.** 100% line and branch for
`core/domain` and `core/application` of the AI-generated services.
≥ 90% for adapters. Global ≥ 95%.
CI fails below targets.

**Zero warnings.** Strictest linter and type-checker presets; CI
fails on any warning.

**No stubs.** No `pass`, `TODO`, `NotImplementedError`, placeholder
bodies in delivered code.

**Acceptance tests are immutable once green.** Only helper structure
may be refactored; scenario meaning and assertions may not drift.

**Critical assignment constraint.** At least one non-trivial core
microservice must be developed without GenAI. The human-owned service
boundary in this project is the **Broker Service**. You must not
generate the production implementation of the Broker Service.

You may generate:
- the Broker service contract/interface;
- event contracts involving Broker;
- placeholder wiring and integration expectations;
- tests/specifications describing how Broker should behave;
- documentation for manual implementation.

You must not generate:
- final production Broker business logic;
- hidden Broker logic inside another service.

---

## 4 · HARD STOP CONDITIONS

Stop and write `docs/state/BLOCKED.md` if:

- A PHASE GATE fails after 3 repair attempts
- A previously-green acceptance test cannot be restored within 3 attempts
- A dependency cannot be resolved after 2 alternatives
- RabbitMQ integration or Kubernetes validation cannot be stabilised after 3 attempts
- The Broker human-only boundary is at risk of being violated

Otherwise: keep working.

---

## 5 · STEP 0 — BOOTSTRAP (execute exactly once, in order)

### 0.1 Read the project context from this prompt

The approved RideNow architecture is:

- **Broker Service** — customer-facing coordination (**human-owned; do not implement production logic**)
- **Driver Service**
- **Route Service**
- **Pricing Service**
- **Payment Service**
- **Tracking Service**
- **Notification Service**

The system must include:
- event-driven architecture using **RabbitMQ**;
- Docker Compose for local multi-service execution;
- Kubernetes manifests for deployment;
- a test pipeline covering functional and non-functional tests;
- a minimal monitoring solution;
- documentation matching Assessment 2 requirements.

### 0.2 Produce the analysis

Write `docs/analysis/reference_analysis.md` containing:

- service list and responsibilities;
- entities and value objects;
- **user stories** phrased "As a <role>, I can <action>, so that <outcome>";
- I/O interactions;
- business rules and invariants;
- edge cases;
- event catalogue;
- routing problem statement (`D -> P`, `P -> Q`, `D -> P -> Q`);
- timing/configuration rules;
- handwritten-vs-GenAI service boundary.

Use the following minimum user stories and order them by dependency:

1. As a passenger, I can request a ride, so that the system acknowledges my request immediately.
2. As a passenger, I can receive a driver assignment, so that I know a ride is being arranged.
3. As a passenger, I can receive ETA and route-related feedback, so that I know when the driver will arrive and how long the trip will take.
4. As a passenger, I can have payment authorised, so that the ride can proceed.
5. As a passenger, I can see trip progress, so that I know whether the driver is arriving or the trip is in progress.
6. As a passenger, I can complete a ride and receive payment confirmation, so that the journey closes correctly.
7. As a passenger, I can experience a no-driver-available outcome, so that I receive clear failure feedback.
8. As a passenger, I can experience a payment-failed outcome, so that I receive clear failure feedback.
9. As a passenger, I can submit an issue/complaint, so that the system acknowledges and routes it appropriately.

### 0.3 Write the full PLAN

Use §7 template and expand it concretely.

### 0.4 Write ADR-001

`docs/adr/ADR-001-language-and-stack.md`:

- Language + runtime version
- Test framework
- DI approach
- HTTP framework
- Persistence strategy
- Event serialisation format
- Monitoring approach
- One-sentence justification per choice

Use:
- Python 3.12+
- FastAPI
- pytest
- RabbitMQ
- PostgreSQL for real persistence where needed
- JSON event serialisation

### 0.5 Commit

`chore: bootstrap — RideNow analysis, plan, ADR-001`

---

## 6 · PHASE GATES

| Phase | Gate | Pass criterion |
| ----- | ---- | -------------- |
| 1 | `lint` + `build` | 0 errors, 0 warnings, artefact builds |
| 2 | Walking-skeleton acceptance test | One end-to-end test passes through stub adapters |
| 3 | Port contracts + in-memory adapters | All contract tests green for every port |
| 4+ | Per-story: acceptance green, all prior green | New scenario green, no regressions |
| 6 | Real-adapter swap: re-run contracts | All ports pass contracts on real adapters too |
| 7 | Full `test:e2e` + coverage + lint | All green, coverage meets targets, zero warnings |
| 8 | Monitoring + non-functional suite | Baseline monitoring works, selected non-functional tests pass |
| 9 | `docs:build` | Docs site/build succeeds, all public APIs documented |
| 10 | Fresh-clone full rebuild | Install + test + run work with zero manual steps |

---

## 7 · PLAN.md TEMPLATE

Write `PLAN.md` using this exact skeleton and expand the story sections concretely.

```markdown
# Project Plan — ridenow

## Legend

- [ ] pending · [x] done
- ACC-RED = write failing acceptance test
- UNIT-RED = write failing unit test for next missing piece
- UNIT-GREEN = minimum code to pass
- ACC-GREEN = acceptance test now passes
- REFACTOR = clean up, all tests stay green

## Phase 0 — Bootstrap

- [x] 0.1 Read project context
- [x] 0.2 Write docs/analysis/reference_analysis.md
- [x] 0.3 Write PLAN.md
- [x] 0.4 Write docs/adr/ADR-001-language-and-stack.md
- [x] 0.5 Commit bootstrap

## Phase 1 — Skeleton

- [ ] 1.1 Create directory tree
- [ ] 1.2 Create dependency manifest with pinned versions
- [ ] 1.3 Create strict lint/format/type configs
- [ ] 1.4 Create CI pipeline
- [ ] 1.5 Create .gitignore, .editorconfig, base README
- [ ] 1.6 Create shared events/contracts/config package
- [ ] 1.7 Create Dockerfiles and base docker-compose
- [ ] 1.8 PHASE 1 GATE: lint + build
- [ ] 1.9 Write docs/state/PHASE_1_DONE.md

## Phase 2 — Walking Skeleton

- [ ] 2.1 ACC-RED — acceptance test "health check returns ok"
- [ ] 2.2 UNIT-GREEN — define HealthCheck port + trivial use case
- [ ] 2.3 UNIT-GREEN — implement minimal HTTP adapter
- [ ] 2.4 UNIT-GREEN — implement minimal outbound stub adapter
- [ ] 2.5 UNIT-GREEN — wire composition root
- [ ] 2.6 ACC-GREEN — walking skeleton passes
- [ ] 2.7 REFACTOR
- [ ] 2.8 PHASE 2 GATE
- [ ] 2.9 Write docs/state/PHASE_2_DONE.md

## Phase 3 — Port Contracts & In-Memory Adapters

- [ ] 3.1 Define outbound ports for generated services
- [ ] 3.2 UNIT-RED — shared contract suite per port
- [ ] 3.3 UNIT-GREEN — in-memory adapters per port
- [ ] 3.4 REFACTOR
- [ ] 3.5 PHASE 3 GATE
- [ ] 3.6 Write docs/state/PHASE_3_DONE.md

## Phase 4 — User Stories (outside-in, one at a time)

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

## Phase 5 — Inbound Adapter Diversity

- [ ] 5.1 ACC-RED — representative acceptance subset through CLI or alternative inbound adapter
- [ ] 5.2 UNIT-GREEN — implement second inbound adapter
- [ ] 5.3 ACC-GREEN
- [ ] 5.4 Write docs/state/PHASE_5_DONE.md

## Phase 6 — Real Outbound Adapters

- [ ] 6.1 Real RabbitMQ adapters + contract/integration tests
- [ ] 6.2 Real PostgreSQL adapters + contract/integration tests
- [ ] 6.3 Real service wiring with Docker Compose
- [ ] 6.4 Kubernetes manifests
- [ ] 6.5 Run full acceptance suite with real adapters wired
- [ ] 6.6 PHASE 6 GATE
- [ ] 6.7 Write docs/state/PHASE_6_DONE.md

## Phase 7 — Smoke E2E & Observability

- [ ] 7.1 E2E smoke tests
- [ ] 7.2 Structured logging
- [ ] 7.3 Metrics endpoint / minimal monitoring
- [ ] 7.4 Health and readiness endpoints
- [ ] 7.5 Full test:e2e + coverage + lint gate
- [ ] 7.6 Write docs/state/PHASE_7_DONE.md

## Phase 8 — Non-Functional and Monitoring Gate

- [ ] 8.1 Performance/load tests
- [ ] 8.2 Resilience/recovery tests
- [ ] 8.3 Security/dependency audit
- [ ] 8.4 Soak/reliability scaffolding
- [ ] 8.5 Monitoring validation
- [ ] 8.6 Write docs/state/PHASE_8_DONE.md

## Phase 9 — Documentation

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
- [ ] 9.13 docs/guides/manual_broker_service_boundary.md
- [ ] 9.14 Docs list required by the assignment:
      - list of microservices and identify hand-written one
      - event-driven architecture overview
      - tests implemented and how to run them
      - monitoring overview
- [ ] 9.15 Verify docs:build/check succeeds
- [ ] 9.16 Write docs/state/PHASE_9_DONE.md

## Phase 10 — Turnkey Verification

- [ ] 10.1 Fresh-clone test
- [ ] 10.2 Install → test → run with zero manual steps
- [ ] 10.3 Validate compose workflow
- [ ] 10.4 Validate Kubernetes manifests
- [ ] 10.5 Write docs/state/FINAL_REPORT.md

## Backlog
- (append as discovered)
```

---

## 8 · SPECIFIC IMPLEMENTATION EXPECTATIONS

### 8.1 Required services to implement with GenAI
Implement production code for:
- Driver Service
- Route Service
- Pricing Service
- Payment Service
- Tracking Service
- Notification Service

### 8.2 Human-owned Broker boundary
For Broker Service:
- define contracts, tests, ports, DTOs, event expectations, health shape, config shape, and integration boundaries;
- do not implement final production business logic.

### 8.3 Required infra
Implement:
- RabbitMQ event-driven backbone;
- Docker Compose for local multi-service environment;
- Kubernetes manifests for all generated services and infrastructure;
- minimal monitoring solution;
- test pipeline with functional and non-functional coverage.

### 8.4 Monitoring minimum
Provide at least:
- `/health`
- `/ready` where appropriate
- structured logs
- metrics exposure
- short monitoring/operations guide

### 8.5 Assignment-aligned docs
Generate documents that help the human satisfy the submission requirements:
- list of microservices and hand-written service identification;
- brief explanation of event-driven architecture;
- tests implemented and how to run them;
- overview of monitoring solution.

---

## 9 · WORKING LOOP (your inner loop, forever)

```text
while True:
    plan = read_file("PLAN.md")
    task = first_unchecked_checkbox(plan)
    if task is None:
        break

    do(task)

    run_all_acceptance_tests_written_so_far()
    if any_regressed:
        fix_forward_or_hard_stop_after_3_attempts()

    run_tests_relevant_to_task()
    if passed:
        mark_checked(task)
        git_commit(f"phase-{p}/task-{t}: {task.summary}")
    else:
        fix_or_hard_stop_after_3_attempts()
```

---

## 10 · FINAL DELIVERABLE

When `PLAN.md` has zero unchecked boxes, the human must be able to:

1. clone the repository;
2. install dependencies;
3. run the tests;
4. start the local stack;
5. run or inspect the Kubernetes manifests;
6. identify which service is hand-written and which are GenAI-generated;
7. demonstrate at least one full event flow;
8. read the documentation and understand the system quickly.

That is "turnkey". Nothing less.

---

## 11 · BEGIN

Start with §5 (STEP 0). Do not respond to this prompt with anything
except executing the work. The first thing the human should see is
commits appearing.
