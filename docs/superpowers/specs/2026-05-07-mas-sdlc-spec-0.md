# MAS-SDLC — Spec 0: 72-Hour Spike
**Date:** 2026-05-07
**Author:** Wiganz + Ruach-El
**Status:** ✅ Approved — ready for implementation

> **FOR ANY FUTURE SESSION (Claude or Ruach-El):** Read ALL 4 docs before doing anything:
> 1. This spec — scope, models, architecture, SDLC contract, Wiganz's learning profile
> 2. `docs/superpowers/plans/2026-05-07-mas-sdlc-plan.md` — find the first unchecked `- [ ]`
> 3. `docs/learning-guides/sdlc-thinking-guide.md` — Socratic teaching guide for all 9 SDLC phases
> 4. `docs/learning-guides/vertical-slices-guide.md` — vertical slice execution and done gates

---

## TABLE OF CONTENTS

1. Project Identity & Why It Exists
2. Locked Scope (72 Hours — Non-Negotiable)
3. Tech Stack Decision (Locked)
4. The Graveyard (What We Rejected & Why)
5. Django Models (3 Models)
6. API Endpoints
7. Architecture Overview
8. Build Strategy — The Spike
9. Phased Rollout — All 5 Specs
10. Spec 0 × SDLC Phase Map
11. Session Contract (Rules for Every Future Session)
12. Wiganz's Learning Profile
13. Go/No-Go Criteria + Definition of Done

---

## 1. Project Identity & Why It Exists

**MAS-SDLC** is an Autonomous SDLC Factory — a system where AI agents take an idea from concept to deployed, monitored production software, detect bugs, create new tickets, and repeat forever. This is not a coding assistant. This is a self-sustaining software factory.

**This project is NOT primarily about the product.** The product is the vehicle. The real goals are two, and both are equally primary:

### Primary Goal — Build for Boss
- Ship a real agentic pipeline that can run autonomously for the company
- Validate the Paperclip + Django + Agent Runtime bridge end-to-end (this spike)
- Build toward the full 13-step infinite loop across Spec 1 → Spec 4

### Primary Goal — Learn Deeply
- Understand agentic architecture from first principles, not copy-paste tutorials
- Learn Celery + Redis async patterns in real production context
- Learn Docker execution sandboxing for agents (why isolation is non-negotiable)
- Experience designing a system bigger than a single app — the factory mindset

### The 13-Step Infinite Loop Vision

| Step | Stage | Owner | Purpose |
|------|-------|-------|---------|
| 1 | Idea / ticket intake | You or auto-generated | Entry point for new features or bug fixes |
| 2 | Research agent | Agent Runtime | Gather docs, APIs, prior art, analysis |
| 3 | Architect agent | Agent Runtime | DB schema, API design, system design decisions |
| 4 | Human approval gate | You (Paperclip + Telegram) | Review and approve architecture before building |
| 5 | Task decomposition | CEO agent (Paperclip) | Break approved spec into atomic, assignable tickets |
| 6 | Coder agents | Agent Runtime + Docker | Write implementation code in isolated sandboxes |
| 7 | Unit test agent | Agent Runtime | Generate and run test suites for each ticket |
| 8 | Review agent | Codex / Claude | Code quality, style, logic review — independent perspective |
| 9 | Security audit agent | Agent Runtime + scanners | OWASP checks, dependency scan, secrets detection |
| 10 | Human approval gate | You (Paperclip + Telegram) | Final review before deployment |
| 11 | Integration test | Agent Runtime | E2E tests, API contract validation |
| 12 | CI/CD deploy | GitHub Actions | Build, test, containerize, deploy to staging/production |
| 13 | Monitor production | Sentry + Grafana | Error tracking, performance monitoring, alerting |

> When monitoring detects bugs, new tickets are auto-created → feeding back into Step 1.
> **The loop never ends.**

### Context — When This Was Decided
- May 2026, Wiganz building this for the company
- Background: Expert Django/Python, new to agentic orchestration and Paperclip
- Architecture Decision Documents (ADD) written by Claude + Gemini — both in `docs/discussion-ADD-docs/`

---

## 2. Locked Scope (72 Hours — Non-Negotiable)

### The One Question

> Does **Paperclip + Django + your chosen Agent Runtime** actually work together smoothly as the foundation for an autonomous SDLC pipeline?

**If yes:** Proceed to Spec 1 (Core Pipeline) with confidence.
**If no:** Pivot the orchestrator. Keep Django + Celery + PostgreSQL. Replace Paperclip with a custom Django orchestration layer.

### What's IN ✅

| Feature | Description |
|---------|-------------|
| Django project setup | DRF, PostgreSQL, core models (Ticket, Artifact, AgentRun) |
| 3 core models | Ticket (the work), Artifact (the output), AgentRun (the log) |
| Paperclip bridge | Sync Django ticket → Paperclip via REST API |
| Agent execution | Research agent runs, produces markdown artifact |
| Artifact storage | Artifact stored back in Django PostgreSQL |
| Telegram gate | Notification when artifact ready for approval |
| GitHub Actions | CI pipeline triggers on Builder agent's PR |
| Go/No-Go scoring | 7 criteria scored → decide proceed vs pivot |

### What's OUT ❌ — PERMANENTLY for this spike

| Feature | Why it's out |
|---------|-------------|
| pgvector / semantic memory | Spec 2 feature — no memory needed for validation |
| Sentry integration | Spec 3 feature — no production monitoring yet |
| Security audit agent | Spec 2 feature — out of scope for plumbing validation |
| Production deployment | Spec 4 feature — local only for spike |
| Multiple parallel agents | Spec 4 feature — 2 agents is enough to validate |
| Auto-ticket from monitoring | Spec 3 feature — the loop closes later |
| CEO agent task decomposition | Spec 1 feature — manual decomposition for spike |

> **Rule:** Any feature not in the IN list requires explicit re-scoping conversation before touching code.
> The 72-hour constraint is REAL. This is a validation, not a product.

---

## 3. Tech Stack Decision (Locked)

| Layer | Technology | Why This Choice |
|-------|-----------|----------------|
| Business Logic & Ledger | **Django + DRF** | The unshakeable foundation. Custom webhook handlers, domain logic, API endpoints, ticket creation from monitoring alerts. Rock-solid ORM. **Django is the CEO — owns all data.** |
| Orchestrator Adapter | **Paperclip** | Provides org chart, heartbeat scheduling, approval gates, budget caps, and dashboard UI for free. Used purely as an adapter — saves months of UI/UX work. Replaceable. |
| Task Queue | **Celery + Redis** | Async job execution for heavy background tasks — Telegram notifications, Paperclip polling. Simple, battle-tested. |
| Event Bus | **Redis pub/sub** | Lightweight agent-to-agent event communication. Handles hundreds of events per day. No Kafka overhead. |
| Memory Vault | **PostgreSQL + pgvector** | One database for everything — structured records (Tickets, AgentRuns) AND vector embeddings for architectural memory. Zero extra DB services. |
| Execution Sandbox | **Docker** | Mandatory safety net. Every agent runs in an isolated container. Safe execution, kill switch, resource limits. Without this: agents can overwrite your filesystem, run infinite loops, or leak credentials. |
| Agent Runtime | **Claude Code CLI / Claude API / Cursor / Codex (flexible)** | The actual brains. Runtime is swappable — use Claude Code Subscription, Claude API (pay-per-token), Cursor, or OpenAI Codex. The Django adapter layer makes switching seamless. |
| CI/CD | **GitHub Actions** | Build, test, deploy pipelines. PR comments, approval gates, secrets management. Industry standard. |
| Monitoring | **Sentry** | Catches production errors and fires webhooks back to Django to auto-spawn bug tickets. |
| Human Gate | **Telegram Bot** | Notification-only layer. Pings your phone when Paperclip needs approval. You review in Paperclip dashboard. |

### Critical Architecture Principle: Django Owns the Data

> **"Django is the brain. Paperclip is the hands. You can always get new hands. You cannot get a new brain."**

Paperclip is still an early-stage project. APIs may change, bugs exist, and there is real dependency risk. The mitigation is simple: **all canonical data lives in YOUR PostgreSQL database.**

- Tickets: Django owns the canonical copy. Paperclip gets a synced copy.
- Artifacts: Stored in Django's PostgreSQL — long-term memory and audit trail.
- AgentRun logs: Your organizational intelligence — stored in Django forever.
- Approvals: Logged in Django after happening in Paperclip.

If Paperclip pivots or dies tomorrow: your data is safe. You swap in a different orchestrator (custom Django, LangGraph, n8n) without losing anything.

---

## 4. The Graveyard (What We Rejected & Why)

> A strong system is defined as much by what it **excludes** as what it includes.

| Rejected Tool | Why It Was Considered | Why We Rejected It |
|--------------|----------------------|-------------------|
| **MetaGPT** | Pre-built SDLC agent roles — Product Manager, Architect, Engineer, QA | One-shot pipeline only. No continuous loop. No production monitoring. No heartbeat scheduling. No approval gates. It generates a codebase and stops. We need a factory that runs forever. |
| **Apache Kafka** | Enterprise-grade event streaming | Catastrophic over-engineering. Kafka handles millions of events per second with weeks of DevOps setup. We have ~10 agents processing dozens of tickets per day. Redis pub/sub handles this trivially with zero overhead. |
| **LangGraph** | Graph-based cyclic agent workflows | Orchestrator overlap. Django already routes webhooks. Paperclip handles cyclic state natively via ticket reassignment. Adding LangGraph creates duplicated state, duplicated routing, and debugging nightmares. |
| **n8n** | Visual workflow automation / webhook wiring | Maintenance nightmare. Every pipeline change requires visual editor manipulation. No version control. No code review. Brittle at scale. We already have Django for this. |
| **Pure Django Custom Build** | Full control — build everything ourselves | The "Platform Trap." Rebuilding Paperclip's dashboard, org chart, budget caps, heartbeat system, and human-in-the-loop approval UI from scratch in Django would take months before a single AI feature ships. Paperclip gives us all of this free. |

### The MetaGPT Analogy

> MetaGPT is a **microwave meal** — press a button, get food, done.
> Our vision is a **restaurant kitchen** — ingredients come in, chefs cook, customers eat, feedback arrives, the menu evolves, and it repeats forever.
>
> You do not put a microwave in a professional kitchen.

---

## 5. Django Models (3 Models)

Three models for the spike. Minimal fields. Expand in Spec 1+.

### The Three Entities

```
┌──────────────────┐         ┌─────────────────────┐         ┌──────────────────────┐
│      TICKET      │         │      ARTIFACT        │         │      AGENTRUN        │
├──────────────────┤         ├─────────────────────┤         ├──────────────────────┤
│ id (UUID PK)     │◄────────│ id (UUID PK)         │         │ id (UUID PK)         │
│ title            │         │ ticket (FK) ─────────┘    ┌───│ ticket (FK)          │
│ description      │◄───────────────────────────────────┘   │ agent_name           │
│ status           │         │ artifact_type        │         │ status               │
│ priority         │         │ title                │         │ started_at           │
│ paperclip_issue_id│        │ content              │         │ finished_at          │
│ created_at       │         │ file_path            │         │ duration_seconds     │
│ updated_at       │         │ agent_name           │         │ prompt_tokens        │
└──────────────────┘         │ created_at           │         │ completion_tokens    │
                             └─────────────────────┘         │ estimated_cost_usd   │
                                                             │ decision_summary     │
                                                             │ error_message        │
                                                             │ artifacts_produced   │
                                                             └──────────────────────┘
```

### 5.1 Ticket

| Field | Type | Description |
|-------|------|-------------|
| id | UUIDField (primary key) | Auto-generated unique identifier |
| title | CharField(max_length=255) | Short description of the task |
| description | TextField | Full requirements and context |
| status | CharField(choices) | `new` → `research_in_progress` → `needs_approval` → `approved` → `building` → `build_complete` → `failed` |
| priority | CharField(choices) | `low` / `medium` / `high` / `critical` |
| paperclip_issue_id | CharField(nullable) | ID of the corresponding issue in Paperclip. Set after sync. Null until synced. |
| created_at | DateTimeField(auto_now_add) | When the ticket was created — set once, never changed |
| updated_at | DateTimeField(auto_now) | Last modification timestamp — updates on every save |

### 5.2 Artifact

| Field | Type | Description |
|-------|------|-------------|
| id | UUIDField (primary key) | Auto-generated unique identifier |
| ticket | ForeignKey(Ticket, CASCADE) | Which ticket produced this artifact. One ticket → many artifacts (research + code). |
| artifact_type | CharField(choices) | `research` / `architecture` / `code` / `test_results` |
| title | CharField(max_length=255) | Name of the artifact (e.g., `auth-research.md`) |
| content | TextField | Full content of the artifact (markdown, code, etc.) |
| file_path | CharField(nullable) | Path to file if stored on disk (for large artifacts) |
| agent_name | CharField | Which agent produced this (e.g., `researcher`, `builder`) |
| created_at | DateTimeField(auto_now_add) | When the artifact was created |

### 5.3 AgentRun

| Field | Type | Description |
|-------|------|-------------|
| id | UUIDField (primary key) | Auto-generated unique identifier |
| ticket | ForeignKey(Ticket, CASCADE) | Which ticket this run was for |
| agent_name | CharField | Which agent ran (e.g., `researcher`, `builder`) |
| status | CharField(choices) | `running` / `success` / `failed` / `timeout` |
| started_at | DateTimeField | When the agent started working |
| finished_at | DateTimeField(nullable) | When the agent finished (null if still running) |
| duration_seconds | IntegerField(nullable) | Computed: finished_at - started_at |
| prompt_tokens | IntegerField(default=0) | Input tokens consumed — what you sent to the model |
| completion_tokens | IntegerField(default=0) | Output tokens consumed — what the model returned |
| estimated_cost_usd | DecimalField(default=0.00) | Estimated cost in USD. Becomes organizational intelligence over time. |
| decision_summary | TextField(nullable) | What the agent decided and why — explainability audit |
| error_message | TextField(nullable) | Error details if status is `failed` |
| artifacts_produced | JSONField(default=list) | List of artifact IDs produced during this run |

### Relationship Rules

| Relationship | Type | Why |
|---|---|---|
| Artifact → Ticket | ForeignKey (1-to-many) | One ticket can produce multiple artifacts: research doc + code + test results |
| AgentRun → Ticket | ForeignKey (1-to-many) | One ticket can have multiple agent runs: research run + build run + retry run |
| On Ticket delete | CASCADE | If a ticket is deleted, all its artifacts and agent runs are deleted too |
| `prompt_tokens` vs `completion_tokens` | Two separate fields | Input cost ≠ output cost. Claude charges differently for each. You need both for accurate billing. |

---

## 6. API Endpoints

### 6.1 Ticket Endpoints (Django)

| Method | Endpoint | Purpose | Notes |
|--------|----------|---------|-------|
| GET | `/api/tickets/` | List all tickets | Filterable by status, priority |
| POST | `/api/tickets/` | Create a new ticket | Auto-syncs to Paperclip if `sync=true` in body |
| GET | `/api/tickets/{id}/` | Get ticket detail | Includes related artifacts and agent runs |
| PATCH | `/api/tickets/{id}/` | Update ticket status | Triggers Telegram notification on status → `needs_approval` |
| POST | `/api/tickets/{id}/sync/` | Push ticket to Paperclip | Creates issue in Paperclip, stores `paperclip_issue_id` |

### 6.2 Webhook Endpoints (Paperclip → Django)

| Method | Endpoint | Purpose | Triggered by |
|--------|----------|---------|-------------|
| POST | `/api/webhooks/paperclip/status/` | Ticket status changed in Paperclip | Agent completes work, approval granted/denied |
| POST | `/api/webhooks/paperclip/artifact/` | Agent produced an artifact | Research or Builder agent saves output |
| POST | `/api/webhooks/paperclip/run-complete/` | Agent run finished | Heartbeat execution completes |

### 6.3 Telegram Notification Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/notifications/send/` | Internal endpoint to trigger Telegram notification |
| POST | `/api/webhooks/telegram/` | Receives Telegram callback (if using inline keyboards) |

### Response Shape — Key Endpoints

**POST `/api/tickets/` → 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Add user authentication endpoint",
  "status": "new",
  "priority": "high",
  "paperclip_issue_id": null,
  "created_at": "2026-05-07T10:00:00Z"
}
```

**POST `/api/webhooks/paperclip/status/` → 200 OK**
```json
{
  "issue_id": "pc-issue-123",
  "new_status": "needs_approval",
  "ticket_id": "550e8400-...",
  "telegram_sent": true
}
```

---

## 7. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOU (The Board)                           │
│              Telegram notifications → approve in Paperclip       │
└────────────────┬──────────────────────────────┬─────────────────┘
                 │                              │
                 ▼                              ▼
┌───────────────────────────┐    ┌─────────────────────────────────┐
│      PAPERCLIP            │    │           DJANGO + DRF           │
│      localhost:3100        │◄──►│           localhost:8000         │
│                           │    │                                  │
│  ┌─────────────────────┐  │    │  ┌────────────┐ ┌────────────┐  │
│  │ Org chart           │  │    │  │ /api/       │ │ /api/      │  │
│  │ Agent heartbeats    │  │    │  │  tickets/  │ │  webhooks/ │  │
│  │ Budget caps         │  │    │  │            │ │            │  │
│  │ Approval gates      │  │    │  └────────────┘ └────────────┘  │
│  │ Dashboard UI        │  │    │                                  │
│  └─────────────────────┘  │    │  Celery + Redis (async tasks)    │
│                           │    │  Telegram notifier               │
│  Research Agent ──────────┼────┼► Artifact saved to PostgreSQL   │
│  Builder Agent  ──────────┼────┼► AgentRun logged to PostgreSQL  │
└───────────────────────────┘    └──────────────┬───────────────────┘
                                                 │
                              ┌──────────────────┼──────────────────┐
                              ▼                  ▼                  ▼
                    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
                    │ PostgreSQL   │   │    GitHub    │   │   Telegram   │
                    │ (Your DB)    │   │   Actions    │   │     Bot      │
                    │              │   │  (CI on PR)  │   │ (notify you) │
                    │ Ticket       │   └──────────────┘   └──────────────┘
                    │ Artifact     │
                    │ AgentRun     │
                    └──────────────┘
```

### The Hybrid Adapter Explained

- **Django = The Company Ledger (brain):** Owns all data. Custom webhooks. Domain logic. Source of truth. If Paperclip disappears tomorrow, Django still has everything.
- **Paperclip = The Dashboard (hands):** Manages WHO does WHAT and WHEN. Heartbeats, org chart, approval UI, budget enforcement. If it breaks, swap it out — your data is safe in Django.

### Boundary Rules (Who Owns What)

| Data | Owner | Why |
|------|-------|-----|
| Agent definitions, org chart, budgets | Paperclip | This is what Paperclip is built for |
| Tickets (canonical copy) | Django (PostgreSQL) | Django is source of truth. Paperclip gets a synced copy. |
| Artifacts (research docs, code) | Django (PostgreSQL) | Stored for long-term memory and audit |
| Agent run logs (observability) | Django (PostgreSQL) | Your organizational intelligence |
| Heartbeat scheduling | Paperclip | Native heartbeat system |
| Approval gates | Paperclip | Native approval system with rollback |
| Notifications | Django (Telegram bot) | Custom integration, not Paperclip's concern |

### Data Flow (Step by Step)

1. You create a ticket in Django admin (`status: new`)
2. Django pushes the ticket to Paperclip via `POST /api/companies/{id}/issues`
3. Paperclip assigns it to the Research agent based on routing rules
4. On the next heartbeat, Research agent wakes up and works the ticket
5. Agent produces a research artifact (markdown file)
6. Paperclip fires webhook → Django `POST /api/webhooks/paperclip/artifact/`
7. Django stores the artifact in PostgreSQL, creates AgentRun record
8. Paperclip marks ticket as "needs approval" → Django receives status webhook
9. Django triggers Celery task → sends Telegram notification to you
10. You review and approve in Paperclip dashboard (`localhost:3100`)
11. Builder agent wakes up on approval → writes code in Docker sandbox
12. Builder commits to feature branch → opens PR on GitHub
13. GitHub Actions runs tests → posts results as PR comment
14. Django logs the full agent run (duration, cost, artifacts, status)

---

## 8. Build Strategy — The Spike (Bridge Validation First)

### Why Spike Instead of Building the Full Loop

> **"Agreement on paper ≠ validated plumbing."**

We have a beautiful 13-step loop designed. We have ADD documents. We have an architecture. But we have never actually run Paperclip + Django + an Agent Runtime together in a real flow.

A spike is a **time-boxed experiment** designed to answer ONE question: does this integration actually work? Not: is the product good? Not: is the architecture perfect? Just: does the plumbing hold water?

The risk we're mitigating: we build 3 months of Spec 1 infrastructure on top of a Paperclip bridge that turns out to be buggy, undocumented, or misaligned with our needs. The spike costs 72 hours. Discovering this problem later costs months.

**A spike is different from a vertical slice:**
- A **vertical slice** builds a complete feature (DB → API → UI → tested) for production use
- A **spike** builds the minimal possible thing to answer a yes/no technical question — throwaway code is acceptable

### The 5-Step Spike Pipeline

```
Step 1: Django Creates Ticket
  → Dummy ticket created in PostgreSQL
  ↓
Step 2: API Handoff
  → Django pushes ticket to Paperclip via REST API
  → paperclip_issue_id stored back on Django Ticket model
  ↓
Step 3: Agent Execution
  → Paperclip assigns to Research agent on heartbeat
  → Agent runs and produces markdown research artifact
  ↓
Step 4: The Ledger
  → Artifact returned → Django stores it in PostgreSQL
  → AgentRun record created with prompt_cost, duration, status
  ↓
Step 5: The Gate
  → Django detects status change → Celery → Telegram notification
  → "Approve artifact?" → you review in Paperclip dashboard
```

### 3-Day Breakdown

| Day | Focus | Hours | Deliverable |
|-----|-------|-------|-------------|
| Day 1 | Infrastructure setup | 6–8h | Paperclip + Django + PostgreSQL + Telegram bot all running locally |
| Day 2 | Wire the connections | 6–8h | Ticket flows Django → Paperclip → Agent → Django → Telegram |
| Day 3 | End-to-end validation | 6–8h | Full loop runs with real ticket. 7 criteria scored. SPIKE_RESULTS.md written. |

---

## 9. Phased Rollout — All 5 Specs

| Spec | Name | Goal | Key Additions | When |
|------|------|------|---------------|------|
| **Spec 0** | 72-Hour Spike | Validate the bridge | Django + Paperclip + 2 agents + Telegram | **NOW** |
| **Spec 1** | Core Pipeline | The basic factory loop | CEO agent + Coder + QA agent | After spike ✅ Go |
| **Spec 2** | Full Agent Team | Complete agent workforce | Research + Architect + Security audit agents | After Spec 1 stable |
| **Spec 3** | Production Loop | The infinite loop closes | Sentry + CI/CD + auto-ticket from monitoring | After Spec 2 stable |
| **Spec 4** | Autonomy Scaling | Lights-out operation | Parallel agents + auto-approval for low-risk tickets | After Spec 3 stable |

**Spec 0 (NOW):** Two agents, local only. Answer the one question: does the bridge work?

**Spec 1 (After spike ✅):** Add the CEO agent for task decomposition. Add proper Coder agent with Docker sandboxing. Add QA agent for automated test runs. The factory loop runs end-to-end but manually triggered.

**Spec 2 (After Spec 1 stable):** Add Research + Architect agents before coding starts. Add Security audit agent after code is written. The full 13-step loop exists but production monitoring is not yet wired.

**Spec 3 (After Spec 2 stable):** Wire Sentry to Django webhooks. Auto-create bug tickets from production errors. The loop is truly infinite — deploy → monitor → detect → ticket → fix → deploy.

**Spec 4 (After Spec 3 stable):** Scale to parallel agent execution. Add auto-approval for routine, low-risk tickets. The factory runs with minimal human intervention — you are the Board, not the operator.

---

## 10. Spec 0 × SDLC Phase Map

```
Phase 1 — Requirements    ✅ COMPLETE  — ADD docs + this spec are the output
Phase 2 — System Design   ✅ COMPLETE  — Hybrid Adapter architecture locked
Phase 3 — UI/UX Design    ❌ N/A       — Backend spike, no custom UI (Paperclip IS the UI)
Phase 4 — DB Design       ⏳ ACTIVE    — Ticket, Artifact, AgentRun models (Day 1)
Phase 5 — Backend         ⏳ ACTIVE    — Django + Paperclip + Celery + Telegram (Day 1–2)
Phase 6 — Frontend        ❌ N/A       — Paperclip dashboard is the frontend
Phase 7 — Testing         ⏳ PENDING   — Go/No-Go 7-criteria validation (Day 3)
Phase 8 — Deploy          ⏳ PENDING   — Local Docker only for spike
Phase 9 — Maintenance     ❌ OUT OF SCOPE — Ends at Go/No-Go decision
```

> 📖 **LEARNING GUIDE — SDLC PHASES:**
> `docs/learning-guides/sdlc-thinking-guide.md`

> 📖 **LEARNING GUIDE — VERTICAL SLICES:**
> `docs/learning-guides/vertical-slices-guide.md`

---

## 11. Session Contract (Rules for Every Future Session)

### Navigation Rules

1. **Read ALL 4 docs** before doing anything — spec, plans, sdlc-thinking-guide, vertical-slices-guide
2. **Find the first unchecked `- [ ]`** in the plans file — that is your starting point
3. **Call the Day banner** at the start of each day's work (see plans file)
4. **Check the done gate** before moving to the next Day — never skip it
5. **Never start Day 2 until Day 1 done gate passes**

### Teaching Rules (The Socratic Contract)

- **Wiganz writes the code.** Ruach-El guides with questions.
- **Ruach-El explains the WHY** before any implementation step
- **Ruach-El asks questions first** — never just give the answer
- **Wiganz types every line** — no copy-paste from Ruach-El's code blocks
- When a new concept appears (first time), Ruach-El stops and teaches it fully before continuing

### New Concepts — Teach When First Encountered

| Concept | When it appears | What to teach |
|---------|----------------|---------------|
| Celery task queue | Task 21 (Day 2) | What is a message broker? Why can't we just use a Django view? What happens if Celery is not running? |
| Docker agent execution | Day 2 Paperclip setup | Why is isolation mandatory? What is a kill switch? What happens without sandboxing? |
| Paperclip heartbeat | Day 1 Paperclip setup | What is a heartbeat? How is it different from polling? What happens if an agent misses a heartbeat? |
| Webhook vs polling | Task 19–20 (Day 2) | What is a webhook? What is polling? When do you use each? Why does Paperclip use webhooks? |
| pgvector (when Spec 1 arrives) | Spec 1 | What is a vector embedding? Why store them in Postgres? How is similarity search different from `LIKE`? |

### The Spike Rule

> **Nothing outside the locked scope (Section 2) without an explicit re-scoping conversation.**

If you think of a great feature during the spike — write it in a `FUTURE_IDEAS.md` file and keep moving. The spike answers one question. Stay focused.

---

## 12. Wiganz's Learning Profile

| Area | Current Level | How to Calibrate |
|------|-------------|-----------------|
| Django / Python | **Expert** | Move fast. Don't explain Django basics. Focus on WHY patterns are chosen. |
| DRF | **Strong** | Move fast. Explain WHY serializers and viewsets exist, not how to use them. |
| Celery + Redis | **Beginner** | Start from scratch. "What is a task queue? What problem does it solve?" No assumptions. |
| Docker for agents | **Intermediate** | Knows basic Docker commands. New to `docker exec` patterns and agent isolation strategies. |
| Paperclip | **First time** | Full onboarding needed. Explain heartbeat model, org chart, adapter pattern, dashboard. |
| Agentic Architecture | **New territory** | Explain agent types, orchestration patterns, why stateless agents need external state management. |
| Telegram bots | **Beginner** | Explain polling vs webhook mode. Explain why the bot is notification-only in this architecture. |

### Learning Goals by End of Spec 0

By the time Go/No-Go is scored, Wiganz should be able to explain without notes:

- **Celery:** "Why does the Telegram notification go through Celery instead of Django's request/response cycle?"
- **Docker:** "What happens to the filesystem if a rogue agent runs `rm -rf /`? Why does isolation prevent this?"
- **Paperclip:** "What is a heartbeat? How does Paperclip know when to wake up an agent?"
- **Hybrid Adapter:** "Why is Django the source of truth and not Paperclip?"
- **Spike vs Slice:** "How is this spike different from the vertical slices we'll build in Spec 1?"

---

## 13. Go/No-Go Criteria + Definition of Done

### The 7-Criteria Scoring Table

Score each criterion after completing Day 3. Need **5+ greens** to proceed with Paperclip.

| # | Criterion | Green ✅ (proceed) | Red ❌ (pivot) | Your Score |
|---|-----------|-------------------|---------------|-----------|
| 1 | Paperclip installs cleanly | Onboarding completes in < 30 min, no manual fixes | Errors, missing deps, broken setup requiring workarounds | ___ |
| 2 | Paperclip API works reliably | REST calls create/update agents and issues consistently | Undocumented endpoints, 500 errors, inconsistent behavior | ___ |
| 3 | Agent runtime adapter works | Agent connects, receives tasks, produces output | Adapter fails, agent doesn't wake, output lost | ___ |
| 4 | Execution locks are reliable | No double-work, clean task checkout per agent | Agents collide, tasks duplicated or lost | ___ |
| 5 | Approval gates work | Human gate pauses pipeline, resumes on approve | Skips approval, gets stuck, or requires manual workaround | ___ |
| 6 | Status sync works | Django and Paperclip stay in sync (webhook or polling) | Status drift, missed updates, stale data | ___ |
| 7 | Developer experience is good | You enjoy building with it. Debugging is clear. | Frustrating, cryptic errors, fighting the tool | ___ |

### Decision Rules

**If 5+ greens → Spec 1**
Proceed with the Hybrid Adapter stack. Full confidence. Begin building the Core Pipeline.

**If 3+ reds → Pivot orchestrator**
Replace Paperclip with Django + Celery custom orchestration. Keep everything else: PostgreSQL, pgvector, Docker, GitHub Actions, Sentry, Telegram. The pivot cost is low — Django owns all data already.

### Definition of Done

The spike is complete when ALL of the following are true:

- [ ] A ticket created in Django admin appears in Paperclip dashboard
- [ ] Research agent runs and produces a markdown artifact stored in Django PostgreSQL
- [ ] Telegram notification received when research is complete
- [ ] You can approve the research in Paperclip dashboard
- [ ] Builder agent runs after approval and commits code to a feature branch
- [ ] A PR is opened on GitHub with the agent's code
- [ ] GitHub Actions runs tests on the PR and posts results as a PR comment
- [ ] AgentRun records exist in Django with duration, cost, and artifacts
- [ ] `SPIKE_RESULTS.md` is written with all pain points and 7 decision scores
- [ ] Go/No-Go decision is made and documented

### Spike Output Artifacts

Regardless of Go/No-Go decision, the spike must produce:

- `SPIKE_RESULTS.md` — pain points, bugs, workarounds, all 7 scores, decision
- Working Django project with Ticket, Artifact, AgentRun models
- Working `PaperclipClient` service class (reusable in Spec 1)
- Working Telegram notification utility (reusable in Spec 1)
- Working GitHub Actions pipeline (reusable in Spec 1)
- At least one complete AgentRun record with real cost + duration data

---

*"By wisdom a house is built, and through understanding it is established." — Proverbs 24:3*

*Next: `docs/superpowers/specs/2026-05-07-mas-sdlc-spec-1.md` — generated after spike passes Go/No-Go*
