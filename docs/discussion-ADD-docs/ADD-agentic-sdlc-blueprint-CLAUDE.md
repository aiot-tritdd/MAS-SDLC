# Agentic SDLC Blueprint — Candidate Stack v1

**AUTONOMOUS SOFTWARE COMPANY**

Full Agentic SDLC Blueprint

Architecture Decision Document

Candidate Stack v1

May 2026

*Built with Code **&** Grace*

Multi-AI Synthesis: Claude + GPT + Gemini

---

## Table of Contents

---

## 1. The Vision

### 1.1 What we are building

An autonomous software company — a system where AI agents take an idea from concept to deployed, monitored production software, detect bugs, create new tickets, and repeat forever. This is not a coding assistant. This is a self-sustaining software factory.

### 1.2 The 13-step infinite loop

| **Step** | **Stage** | **Owner** | **Purpose** |
| --- | --- | --- | --- |
| 1 | Idea / ticket intake | You or auto-generated | Entry point for new features or bug fixes |
| 2 | Research agent | Agent Runtime* | Gather docs, APIs, competitor analysis, prior art |
| 3 | Architect agent | Agent Runtime* | Tech stack decisions, DB schema, API design, system design |
| 4 | Human approval gate | You (Paperclip dashboard) | Review and approve architecture before building. Telegram notifies you. |
| 5 | Task decomposition | CEO agent (Paperclip) | Break approved spec into atomic, assignable tickets |
| 6 | Coder agents | Agent Runtime* + Codex | Write implementation code in Docker sandboxes |
| 7 | Unit test agent | Agent Runtime* | Generate and run test suites for each ticket |
| 8 | Review agent | Codex | Code quality, style, logic review |
| 9 | Security audit agent | Agent Runtime* + scanners | OWASP checks, dependency scan, secrets detection |
| 10 | Human approval gate | You (Paperclip dashboard) | Final review before deployment. Telegram notifies you. |
| 11 | Integration test | Agent Runtime* | E2E tests, API contract validation |

> **\*Agent Runtime** is flexible and swappable: Claude Code CLI (Subscription), Claude API (pay-per-token), Cursor, OpenAI Codex, or any LLM provider. The Django adapter layer abstracts the runtime — swap providers without rewriting the pipeline.
| 12 | CI/CD deploy | GitHub Actions | Build, test, containerize, deploy to staging/production |
| 13 | Monitor production | Sentry + Grafana | Error tracking, performance monitoring, alerting |

When monitoring detects bugs or improvement opportunities, new tickets are automatically created, feeding back into Step 1. The loop never ends.

### 1.3 What makes this truly agentic

- Closed-loop: Build → Verify → Ship → Learn → Improve → Repeat
- Self-correcting: QA failure → ticket rejected → reassigned to coder automatically
- Self-healing: Production error → Sentry alert → auto-created bug ticket → agents fix it
- Human-governed: You are the Board of Directors, not the coder

---

## 2. Why Not MetaGPT

### 2.1 What MetaGPT is

MetaGPT is a one-shot pipeline framework. You give it a requirement and it runs through pre-built roles (Product Manager, Architect, Engineer, QA) to generate a codebase. It is impressive for quick prototyping.

### 2.2 Why it fails for our vision

| **Dimension** | **Our Vision** | **MetaGPT** |
| --- | --- | --- |
| Lifecycle | Infinite loop — runs forever | One-shot, done after code generation |
| Feedback loop | Bug → ticket → fix → deploy → repeat | No production loop exists |
| Human gates | You approve in Paperclip dashboard, notified via Telegram | Runs to completion without intervention |
| Agent runtime | Flexible: Claude Code CLI / Claude API / Cursor / Codex with real execution | Internal LLM calls only |
| Budget control | Per-agent spending caps | None |
| Persistence | Agents resume across reboots via heartbeats | Starts fresh every single time |
| Customization | Your roles, your prompts, your routing | Pre-defined roles, rigid structure |
| Deployment | Full CI/CD pipeline to production | Stops at code generation |
| Monitoring | Sentry + Grafana with auto-ticket loop | Does not exist |

### 2.3 The analogy

MetaGPT is a microwave meal — press a button, get food, done. Our vision is a restaurant kitchen — ingredients come in, chefs cook, customers eat, feedback arrives, the menu evolves, and it repeats forever. You do not put a microwave in a professional kitchen.

### 2.4 Could we bolt MetaGPT on?

Technically yes — MetaGPT could handle the spec-to-code portion while Paperclip handles everything else. But this creates two overlapping orchestration layers: two systems deciding who does what, two state machines tracking progress, conflicting task decomposition logic, and double the debugging surface. For a solo developer, this is a maintenance nightmare with no real benefit.

---

## 3. The Hybrid Architecture

### 3.1 Core concept

Two systems, each doing what they are best at, connected by webhooks.

**Paperclip = the CEO layer.** It manages WHO does WHAT, WHEN, and for HOW MUCH. Org charts, dashboards, budgets, approval gates, heartbeat scheduling, audit trails, and execution locks. All free, all built-in.

**Django = the business logic layer.** It handles everything Paperclip cannot: custom webhook integrations (Sentry, GitHub, Grafana), the vector memory system, external service connectors, agent observability logging, and the glue that ties production monitoring back into the agent loop.

**Connection:** They communicate via REST APIs and webhooks. Django does not replace Paperclip. Paperclip does not replace Django. They are two halves of one brain.

### 3.2 The complete tech stack

| **Layer** | **Tool** | **Why this choice** |
| --- | --- | --- |
| Orchestrator | Paperclip | Org chart, agent scheduling, heartbeats, budgets, approval gates, task routing, dashboard UI, audit trails. Free and open-source. Replaceable adapter layer. |
| Business logic | Django + DRF | Your strongest tool. Custom webhook handlers, domain logic, API endpoints, ticket creation from monitoring alerts. Rock-solid ORM and admin panel. |
| Task queue | Celery + Redis | Async job execution for heavy background tasks. Simple, battle-tested, you already know it. |
| Event bus | Redis pub/sub | Lightweight agent-to-agent event communication. Handles hundreds of events per day easily. No Kafka overhead. |
| Agent runtime | Claude Code CLI / Claude API / Cursor / Codex (flexible) | The actual brains. Read code, write code, run commands, review PRs. Runtime is swappable — use Claude Code Subscription, Claude API (pay-per-token), Cursor IDE, OpenAI Codex, or any supported LLM provider. The adapter layer makes switching seamless. |
| Sandboxing | Docker | Every agent runs isolated. Safe execution, kill switch, resource limits, reproducible environments. Mandatory. |
| Memory | PostgreSQL + pgvector | One database for everything. Structured data (tickets, logs, decisions) AND vector search (codebase embeddings, design docs). No extra infra. |
| CI/CD | GitHub Actions | Build, test, deploy pipelines. PR comments, approval gates, secrets, rollback. Simple and robust. |
| Monitoring | Sentry + Grafana | Sentry catches production errors. Grafana shows system health dashboards. Both fire webhooks back to Django. |
| Human comms | Telegram bot | Notification layer only. Pings you when Paperclip needs approval. You review and approve in Paperclip dashboard, not in Telegram. |

### 3.3 Critical architecture principle: Django owns the data

Paperclip is still an early-stage project. APIs may change, bugs exist, documentation is uneven, and there is a real dependency risk. The mitigation is clear:

**Django = source of truth.** Tickets, artifacts, approvals, memory, business rules, agent observability logs — all live in YOUR PostgreSQL database.

**Paperclip = replaceable orchestration adapter.** If Paperclip pivots or dies tomorrow, your data is safe and you swap in a different orchestrator.

Think of it this way: Django is the brain, Paperclip is the hands. You can always get new hands. You cannot get a new brain.

### 3.4 Agent observability logging

Every agent run must be logged in PostgreSQL. Agents are employees — employees need records. This becomes organizational intelligence over time.

| **Field** | **Example** | **Why it matters** |
| --- | --- | --- |
| agent | architect | Which agent ran |
| ticket | 123 | What task it worked on |
| prompt_cost | $0.42 | Token spend per run |
| duration | 4m 12s | Performance tracking |
| decision | Microservice rejected | Agent reasoning audit |
| reason | Monolith better for MVP | Explainability |
| artifacts | spec.md, schema.sql | What was produced |
| status | success / failed / timeout | Health monitoring |

### 3.5 How the two systems connect

Example flow for the auto-ticket feedback loop:

- Production error occurs in your deployed application.
- Sentry catches the error and fires a webhook to Django.
- Django receives the webhook, formats the bug details, and logs the event.
- Django creates a new ticket in Paperclip via Paperclip's REST API.
- Paperclip assigns the ticket to the Research agent on the next heartbeat.
- The entire 13-step loop kicks off again automatically.
- You get a Telegram notification summarizing what happened.

---

## 4. Why This Beats the Alternatives

### 4.1 Tools we explicitly rejected and why

| **Rejected tool** | **Why it was considered** | **Why we rejected it** |
| --- | --- | --- |
| MetaGPT | Pre-built SDLC roles, good for prototyping | One-shot only, no loop, no budget control, no persistence, rigid roles. See Section 2. |
| LangGraph | Handles cyclic agent workflows | Overkill. QA-to-Coder loop is just a ticket state change (failed → reassigned). Paperclip's ticket system handles this natively. |
| Apache Kafka | Enterprise event streaming | Way too heavy for 10 agents and 50 tickets/day. Redis pub/sub handles hundreds of events/sec. Kafka is for millions. |
| n8n | Visual webhook wiring | Becomes a maintenance nightmare at 13 stages. Django IS the glue — one codebase, one deployment, one place to debug. |
| Pinecone / Qdrant | Dedicated vector databases | pgvector gives vector search inside your existing PostgreSQL. One DB, one backup strategy, one auth system. No extra infra. |
| Mixed model families | Different AI models to prevent blind spots | Doubles operational complexity in Phase 1. Start with Claude. Diversify when the pipeline is stable. |
| Build everything custom | Full control, no dependencies | Rebuilding org charts, dashboards, budgets, execution locks, audit trails from scratch takes months. Ship the factory first. |

### 4.2 Comparative summary

| **Dimension** | **Our hybrid** | **Pure Paperclip** | **Pure Django (GPT)** | **CrewAI** | **MetaGPT** |
| --- | --- | --- | --- | --- | --- |
| Matches the vision? | Yes — company | Partially | Yes but months of work | Pipeline only | One-shot only |
| Human gates? | Native | Native | DIY | DIY | None |
| Budget control? | Per-agent | Per-agent | DIY | None | None |
| Feedback loop? | Ticket-based | Ticket-based | DIY | Manual | None |
| Dashboard? | Beautiful (free) | Beautiful | DIY | None | Basic |
| Your language? | Python + JS adapter | JS/TS | Python | Python | Python |
| Time to Phase 1? | 1–2 weeks | 1–2 weeks | 6–8 weeks | 2–3 weeks | 1 week (dead end) |

---

## 5. The 72-Hour Spike Prototype

### 5.1 Why we spike before committing

Three AIs agreeing on a stack means nothing if Paperclip crashes on your machine, its API is painful, or execution locks do not work with your chosen agent runtime in practice. Agreement is not validation. We need hands-on proof.

The spike answers one critical question: Does Paperclip + Django + your Agent Runtime (Claude Code, Claude API, Cursor, Codex, etc.) actually work together smoothly? If yes, full speed ahead. If no, we pivot the orchestrator and keep everything else.

### 5.2 Scope: what we build in 72 hours

A minimal 7-step loop that proves the full architecture works end-to-end:

| **Step** | **What happens** | **Tool** | **Success criteria** |
| --- | --- | --- | --- |
| 1 | Create a ticket manually in Django | Django admin | Ticket saved in PostgreSQL with status "new" |
| 2 | Paperclip picks up the ticket | Paperclip API | Heartbeat fires, Research agent receives task |
| 3 | Research agent runs | Agent Runtime via Paperclip | Agent produces a research artifact (markdown) |
| 4 | Artifact saved back to Django | Webhook: Paperclip → Django | Artifact stored in PostgreSQL, linked to ticket |
| 5 | Telegram notifies you | Telegram bot | You receive a notification that an artifact is ready for review |
| 5b | You approve in Paperclip | Paperclip dashboard | Review artifact, approve or reject in Paperclip's native approval gate |
| 6 | On approval, Builder agent runs | Agent Runtime via Paperclip | Agent writes code and commits to a branch |
| 7 | GitHub Actions runs tests | GitHub Actions | Test results posted back as ticket comment |

### 5.3 What we are NOT building in the spike

- No security audit agent
- No production monitoring or Sentry integration
- No auto-ticket creation loop
- No Grafana dashboards
- No pgvector memory layer
- No multiple parallel coder agents

These all come in later phases. The spike proves the plumbing, not the full pipeline.

### 5.4 Day-by-day plan

#### Day 1: Infrastructure setup

- Install Paperclip locally (npx paperclipai onboard --yes)
- Create a fresh Django project with DRF
- Set up PostgreSQL database with basic models: Ticket, Artifact, AgentRun
- Create a simple Telegram bot for notifications
- Verify Paperclip dashboard loads at localhost:3100
- Create a test company in Paperclip with a CEO agent and one Research agent

#### Day 2: Wire the connections

- Create Django admin action to push a ticket to Paperclip via REST API
- Configure Paperclip to use your chosen agent runtime (Claude Code CLI, Claude API, Cursor, or Codex) as the Research agent adapter
- Set up webhook endpoint in Django to receive artifacts from Paperclip
- Wire Telegram bot to send notifications when Paperclip approval gates are triggered
- Add a Builder agent in Paperclip that triggers on approval
- Test the flow manually: create ticket → research runs → artifact saved

#### Day 3: End-to-end validation

- Run the full 7-step loop with a real ticket (e.g., "Add user authentication endpoint")
- Verify artifact quality — is the research output useful?
- Verify approval flow — does Telegram notification arrive? Can you approve in Paperclip dashboard?
- Verify builder agent — does it commit code to the right branch?
- Verify GitHub Actions — do tests run on the PR?
- Log agent observability data: duration, cost, decision, artifacts
- Document all pain points, bugs, and workarounds discovered

### 5.5 Decision criteria after the spike

| **Question** | **Green (proceed)** | **Red (pivot)** |
| --- | --- | --- |
| Does Paperclip install cleanly? | Onboarding completes in < 30 min | Errors, missing deps, broken setup |
| Does the API work? | REST calls create/update agents and tickets | Undocumented, buggy, or unstable API |
| Does the agent runtime integrate? | Adapter connects, agent runs tasks | Adapter fails, workarounds needed |
| Are execution locks reliable? | No double-work, clean checkout | Agents collide, tasks duplicated |
| Is debugging pleasant? | Clear logs, understandable errors | Black box, cryptic failures |
| Does approval flow work? | Human gate pauses and resumes correctly | Skips approval or gets stuck |
| Is the developer experience good? | You enjoy building with it | Frustrating, fighting the tool |

If you get 5+ greens: proceed with confidence. If you get 3+ reds: keep Django + Celery + Redis, replace Paperclip with a custom orchestration layer built in Django itself. The rest of the stack remains unchanged.

---

## 6. Phased Rollout Plan

### 6.1 Phase 0: The 72-hour spike (Days 1–3)

Prove the plumbing works. See Section 5 for full details.

### 6.2 Phase 1: Basic delegation loop (Weeks 1–2)

**Goal:** CEO + 1 Coder + 1 QA agent. Ticket-to-tested-code working.

- CEO agent decomposes tickets into subtasks
- Coder agent writes implementation in Docker sandbox
- QA agent generates and runs unit tests
- Failed tests → ticket rejected → reassigned to coder (self-correction loop)
- All runs logged in Django with full observability

**Start manually-triggered:** Every step requires your approval. You learn failure modes safely before automating.

### 6.3 Phase 2: Full agent team (Weeks 3–4)

**Goal:** Add Research + Architect + Security agents. Idea-to-reviewed-code pipeline.

- Research agent gathers docs, APIs, and competitor analysis
- Architect agent designs system architecture and DB schema
- Security audit agent runs OWASP checks and dependency scans
- Set up pgvector memory layer for organizational knowledge
- Git branching strategy: one branch per ticket, execution locks prevent collisions
- Begin removing some approval gates as trust builds

### 6.4 Phase 3: Production loop (Weeks 5–6)

**Goal:** Wire CI/CD, monitoring, and the auto-ticket feedback loop.

- GitHub Actions CI/CD pipeline: build → test → containerize → deploy
- Sentry integration: production errors fire webhooks to Django
- Django auto-creates tickets from Sentry alerts
- Grafana dashboards for system health and agent performance
- The infinite loop comes alive: error → ticket → fix → deploy → monitor

### 6.5 Phase 4: Autonomy scaling (Week 7+)

**Goal:** Increase autonomy, add parallel execution, optimize costs.

- Multiple coder agents working on different tickets simultaneously
- QA and Security audit running in parallel
- Selective auto-approval for low-risk changes
- Agent performance analytics: cost per ticket, success rate, time to resolution
- Consider adding model diversity (e.g., Codex for reviews, Claude for architecture)
- Customer feedback integration and business KPI agents (stretch goal)

---

## 7. Known Risks and Mitigations

| **Risk** | **Severity** | **Mitigation** |
| --- | --- | --- |
| Paperclip dependency | HIGH | Django owns all data. Paperclip is a replaceable adapter. 72-hour spike validates before commitment. |
| Token cost explosion | HIGH | Per-agent budgets in Paperclip. Auto-pause at 100%. Claude Code Max subscription ($200/mo) or Claude API pay-per-token or Cursor subscription recommended — choose based on usage pattern. |
| Git merge conflicts | MEDIUM | Branch-per-ticket strategy. Execution locks prevent double-work. Worktrees for parallel agents. |
| Agent hallucination | MEDIUM | QA agent validates all output. Failed tests auto-reject tickets. Human gates at critical points. |
| Infinite fix loops | MEDIUM | Max iteration limit (5 attempts). After limit, escalate to human via Telegram. |
| Paperclip API changes | MEDIUM | Thin adapter layer in Django. API calls abstracted behind a service class. Easy to swap. |
| Docker resource usage | LOW | Resource limits per container. Kill switch for runaway agents. Monitor with Grafana. |
| Telegram bot downtime | LOW | Non-blocking. Agents continue working. Approvals queue until bot recovers. |

---

## 8. Open Questions to Resolve

- Assembly line or selective parallelism? Start sequential, evolve to parallel execution for coder agents on separate tickets. Defined in Phase 4.
- Agent runtime strategy? Multiple options available: Claude Code Max ($200/month flat), Claude API (pay-per-token), Cursor (subscription), OpenAI Codex. Can mix and match — e.g., Claude Code for deep implementation, Codex for independent QA. Evaluate after spike.
- Staging environment strategy? Docker Compose for local staging. Cloud staging (Railway, Fly.io) for production-like testing.
- Customer feedback loop? Not in Phase 1–3. Consider adding analytics + customer voice agents in Phase 4 for a true 10/10 autonomous company.
- Governance constitution? Define which actions agents can take autonomously vs which require human approval. Start strict, loosen over time.
- Multi-company support? Paperclip supports multiple isolated companies per deployment. Useful if this becomes a product you sell.

---

## 9. Final Summary

This document represents the synthesized architecture recommendation from three AI models (Claude, GPT, Gemini), refined through multiple rounds of challenge and counter-argument. The result is a Candidate Stack v1 that balances ambition with pragmatism, speed with safety, and control with autonomy.

The hybrid approach — Paperclip for orchestration, Django for business logic — gives you the fastest path to a working autonomous software factory without rebuilding solved infrastructure or over-engineering with enterprise tools you do not need.

The 72-hour spike is the next concrete action. It proves the architecture with real hands-on validation before any long-term commitment.

Start manually-triggered. Build trust. Automate incrementally. Ship the factory first, optimize the machinery later.

*"Plans fail for lack of counsel, but with many advisers they succeed."*

— Proverbs 15:22

*Built with Code **&** Grace* 🕊️
