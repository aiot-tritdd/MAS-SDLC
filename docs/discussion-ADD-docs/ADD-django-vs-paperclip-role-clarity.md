# Django vs Paperclip — Role Clarity

**What each system actually does in the 13-step loop.**

> Written after reading the full Paperclip server source code and building the 72-hour spike.
> This is the honest answer to: "Do we even need Django if Paperclip does everything?"

---

## The Short Answer

Paperclip runs the factory floor. Django closes the loop.

Without Paperclip — no agents, no execution, no approval gates.
Without Django — the loop never feeds back into itself. You have a pipeline, not a factory.

---

## Step-by-Step: Who Actually Does What

| Step | Stage | Owner |
|------|-------|-------|
| 1 | Idea / ticket intake | You manually **OR Django** receives Sentry/Grafana webhook and auto-creates the ticket |
| 2 | Research agent | **Paperclip** |
| 3 | Architect agent | **Paperclip** |
| 4 | Human approval gate | **Paperclip** dashboard. **Django** sends the Telegram ping so you know to go look |
| 5 | Task decomposition | **Paperclip** CEO agent |
| 6 | Coder agents | **Paperclip** + agent runtime |
| 7 | Unit test agent | **Paperclip** + agent runtime |
| 8 | Review agent | **Paperclip** + agent runtime |
| 9 | Security audit | **Paperclip** + agent runtime |
| 10 | Human approval gate | **Paperclip** dashboard. **Django** sends the Telegram ping |
| 11 | Integration test | **Paperclip** + agent runtime |
| 12 | CI/CD deploy | **GitHub Actions** (runs automatically on branch push) |
| 13 | Monitor production | Sentry + Grafana → **Django** receives webhook → creates ticket → back to Step 1 |

**Paperclip owns Steps 2–11.**
**Django appears at Steps 1, 4, 10, 13 — and as the CI/CD feedback receiver.**

---

## What Paperclip Genuinely Has (Based on Source Code)

Verified by reading all 36 route files in `server/src/routes/`:

- Agents — create, manage, run, org chart, hiring, roles
- Issues/tickets — full lifecycle, status transitions, comments, relations (4563 lines in `issues.ts`)
- Approval gates — human-in-the-loop, pause and resume agents
- Execution workspaces — agents write real files to real git branches
- Budget and cost tracking per agent
- Heartbeat scheduling — agents sleep and resume across reboots
- Activity audit trail
- Dashboard UI, inbox, goals, routines, projects, plugins

For **running agents and managing their work** — Paperclip is complete.

---

## What Paperclip Cannot Do (Confirmed Zero Results in Source)

Searched every route file for these. None exist:

- **Outgoing webhooks to external systems** — Sentry, GitHub Actions, Grafana cannot call into Paperclip
- **Telegram / Slack / email notifications** — Paperclip only notifies inside its own UI
- **Vector memory / pgvector** — no semantic search layer
- **Multi-provider agent adapter** — no abstraction for swapping Claude Code vs Codex

---

## Django's Architectural Role: The Webhook Bridge

Django is the receiver for every external system that needs to talk back into the agent loop.

| External System | What Fires | Django Does | Result |
|---|---|---|---|
| GitHub Actions | test failed webhook | updates ticket, tells Paperclip to reject | coder agent reassigned |
| Sentry | production error webhook | creates new ticket in Paperclip | loop restarts from Step 1 |
| Grafana | alert webhook | creates new ticket in Paperclip | loop restarts from Step 1 |

Without this bridge:
- GitHub Actions test failure sits in GitHub. Coder agent never gets reassigned. You intervene manually.
- Sentry production error sits in Sentry. No new ticket created. Loop dies at Step 12.
- You have a very impressive 12-step pipeline — but still a pipeline, not a factory.

---

## Django's Full Responsibility List

1. **Auto-ticket creation** — receives Sentry/Grafana webhooks, creates Paperclip tickets, closes the infinite loop
2. **Telegram notifications** — pings you at Steps 4 and 10 so you know to go approve in Paperclip
3. **CI/CD feedback** — receives GitHub Actions webhooks, updates ticket status, triggers reassignment
4. **Data sovereignty** — your tickets, artifacts, agent runs, costs in YOUR PostgreSQL — not Paperclip's DB
5. **Agent runtime adapter** — abstraction layer for swapping Claude Code / Codex / Cursor without rewriting the pipeline
6. **pgvector memory** (Phase 2) — codebase embeddings and design doc search inside your own DB

---

## Why Data Sovereignty Matters

From the blueprint (Section 3.3):

> *"Paperclip is still an early-stage project. APIs may change, bugs exist, documentation is uneven."*

Django owns all persistent data. If Paperclip pivots, breaks, or dies:
- Your tickets survive
- Your artifacts survive
- Your agent run history survives
- You swap the orchestrator, keep everything else

Paperclip is a replaceable adapter. Your Django database is not replaceable — it is the source of truth.

---

## The One-Line Summary

**Paperclip runs the agents. Django connects the outside world back into the loop.**

Remove Paperclip — no agents run.
Remove Django — the loop never closes, external systems go unheard, and you're back to creating tickets manually.

Both are load-bearing. Neither replaces the other.

---

*Derived from reading Paperclip server source code (`server/src/routes/`, 36 files) and building the 72-hour spike.*
*Date: May 2026*
