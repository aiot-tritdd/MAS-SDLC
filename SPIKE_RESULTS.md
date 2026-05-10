# SPIKE RESULTS — MAS-SDLC Spike 0

**Date:** 2026-05-10
**Spike Goal:** Validate Paperclip as the AI orchestration layer for the MAS-SDLC pipeline
**Duration:** ~3 days (Day 1–3)
**Decision:** PIVOT ❌ — Paperclip cannot serve as the orchestration backbone

---

## Go/No-Go Scoring (Need 5+ Greens to Proceed)

| # | Criterion | Score | Evidence |
|---|-----------|-------|---------|
| 1 | Paperclip installs cleanly | ✅ GREEN | Server running in ~20 min. Docker-free. No broken deps. |
| 2 | Paperclip API works reliably | ✅ GREEN | `POST /api/companies/:id/issues` creates issues consistently. WIG-7 confirmed in dashboard. |
| 3 | Agent runtime adapter works | ⚠️ YELLOW | HTTP adapter sends payload. Agent connection not fully validated end-to-end. |
| 4 | Execution locks are reliable | ❓ NOT TESTED | Could not reach this phase due to architecture blocker in #6. |
| 5 | Approval gates work | ❓ NOT TESTED | Could not reach this phase due to architecture blocker in #6. |
| 6 | Status sync works | ❌ RED | **Paperclip has ZERO outgoing webhooks.** It cannot notify Django when status changes. Django would need to poll. This is a fundamental architecture mismatch. |
| 7 | Developer experience is good | ⚠️ YELLOW | Docs are sparse. Had to read server source code (`routes/issues.ts`) to understand payload shapes and API behavior. Debugging required source-level inspection. |

**Final Score: 2 Greens, 1 Red, 2 Yellows, 2 Not Tested**
**Decision Rule: 3+ Reds → Pivot. Confirmed 1 Red + architectural blocker preventing remaining criteria from being validatable.**

---

## Critical Finding: No Outgoing Webhooks

**This is the spike's most important discovery.**

Paperclip is designed as a **UI-first tool** where humans drive progress through the dashboard. It has no mechanism to push status changes outward. Specifically:

- No `POST /webhooks` endpoint to register a callback URL
- No event stream / SSE / WebSocket for status subscriptions
- No polling-friendly endpoint that Django can efficiently diff against
- Status changes (backlog → in_progress → needs_approval → done) are UI-driven, not API-driven

**What this means for MAS-SDLC:**
Our Django backend built webhook endpoints (`/api/webhooks/paperclip/status/` and `/api/webhooks/paperclip/artifact/`) expecting Paperclip to call them. Paperclip never will. The entire notification chain — research complete → Django stores artifact → Telegram notified — breaks at the source.

---

## What Did Work (Reusable Artifacts)

Everything we built in Django is sound and reusable regardless of orchestrator:

| Artifact | Status | Reuse in Spec 1? |
|---------|--------|-----------------|
| `core/models.py` — Ticket, Artifact, AgentRun | ✅ Working | YES |
| `core/serializers.py` — TicketSerializer | ✅ Working | YES |
| `core/views.py` — CRUD + webhook endpoints | ✅ Working | YES (swap Paperclip for Celery) |
| `services/paperclip_client.py` — PaperclipClient | ✅ Working | PARTIAL (keep sync_ticket, remove webhook dependency) |
| `core/tasks.py` — sync_ticket_to_paperclip, notify_telegram | ✅ Working | YES |
| `core/tests/test_e2e.py` — full pipeline test | ✅ Passing (2/2) | YES |
| `.env` configuration pattern | ✅ Working | YES |

---

## Bugs and Mistakes Encountered

1. **Wrong `@patch` target** — Two decorators patching same `requests.post` object. Last decorator wins. Fix: mock at task level (`notify_telegram.delay`), not HTTP level.
2. **`CELERY_TASK_ALWAYS_EAGER` deprecated** — Does not work in Celery 5. Tasks don't run eagerly. Fix: mock `sync_ticket_to_paperclip.delay` and call service directly in tests.
3. **`data.get("status")` vs `data.get("new_status")`** — Views read wrong key from webhook payload.
4. **IndentationError** after removing debug print — broke `paperclip_client.py`.
5. **Invented `assigned_to` field** in serializer — doesn't exist on Ticket model.
6. **Company ID not in docs** — Had to discover via `GET /api/companies/` (not documented).

All mistakes are logged in `MAS-SDLC-mistakes.txt`.

---

## Pain Points

- Paperclip documentation does not cover API payload shapes in detail
- No outgoing event system (webhooks, SSE, polling endpoint)
- Company ID is a UUID hidden behind an undocumented API call
- `CELERY_TASK_ALWAYS_EAGER` silently fails in Celery 5 — confusing for debugging
- Agent runtime adapter works one-way only (Django → Paperclip) — no return channel

---

## Decision: PIVOT to Django + Celery Custom Orchestration

**The pivot cost is low.** Django already owns all the data. The models, serializers, tasks, and test infrastructure are solid. Swapping Paperclip for a custom Celery-based orchestrator means:

- Remove: `services/paperclip_client.py` (or repurpose as optional sync)
- Remove: webhook endpoint dependency on Paperclip
- Keep: All models, all Celery tasks, all tests
- Add: Celery task chains for Research → Builder → PR pipeline
- Add: Django admin action for human approval gate
- Add: Status transitions driven by Celery task completion callbacks

**This is the correct call. The data layer is healthy. The orchestration layer needed validation — and the spike delivered that answer.**

---

## What Wiganz Learned (Non-Negotiable Mental Models)

1. **E2E tests mock external services** — Speed + isolated failure ownership
2. **Mock at the task level, not the HTTP level** — `task.delay` not `requests.post`
3. **`@patch` decorator order** — Bottom decorator = first function argument
4. **Serializer = HTTP boundary only** — Service code talks directly to ORM
5. **Read the source before assuming** — Docs lie; `routes/issues.ts` tells the truth
6. **Spike first, build second** — This spike saved weeks of building on a broken foundation

---

*"By wisdom a house is built, and through understanding it is established." — Proverbs 24:3*

*The house we thought we were building needed a different foundation. Now we know.*
