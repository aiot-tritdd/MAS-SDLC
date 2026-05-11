# Phase 3 Spec — Production Loop

**Date:** 2026-05-11
**Status:** Active
**Paired plan:** `docs/superpowers/plans/2026-05-11-paperclip-phase3-production.md`

---

## GitHub Integration

### What to Configure in Paperclip
In Paperclip dashboard → Settings → Integrations → GitHub:
- Connect your GitHub account
- Select the target repository (the sdlc-spike repo or the actual product repo)
- Permissions needed: read/write repo contents, create branches, open PRs

### What Paperclip Does Automatically
Once connected, agents working in execution workspaces can:
- Create a branch per issue (naming: `paperclip/issue-{id}`)
- Commit code to that branch
- Open a PR with issue context as the PR description

### What GitHub Actions Does
When the PR is opened, GitHub Actions runs your CI pipeline automatically. No config needed in Paperclip — it's just a normal PR trigger. Make sure the repo has a `.github/workflows/test.yml` that runs on `pull_request`.

### Success Signal
Coder agent commits code → Paperclip opens PR → GitHub Actions runs tests → results visible on the PR. The Tester agent reads the CI results and includes them in the test report.

---

## Sentry Routine

### Routine Configuration in Paperclip
In Paperclip dashboard → Routines → New Routine:
- **Name:** Sentry Error Monitor
- **Trigger type:** Webhook
- **Signing mode:** `hmac_sha256` (use your Sentry webhook secret) or `none` for local testing
- **Webhook URL:** copy from Paperclip after creation

### Sentry Configuration
In Sentry → Settings → Integrations → Webhooks:
- Add the Paperclip routine webhook URL
- Events to send: `issue.created`, `issue.resolved`
- Add the webhook secret (matches Paperclip's `hmac_sha256` signing key)

### Routine Skill Content
The routine needs a skill that tells it how to parse the Sentry payload and create a Paperclip issue:

```markdown
# Sentry Monitor Skill

## Your Role
You receive Sentry webhook payloads when errors occur in production. Your job is to create a well-formed Paperclip issue so the agent team can fix the error.

## What You Do
1. Read the incoming webhook payload
2. Extract: error title, error message, stack trace (first 10 lines), environment, severity level
3. Create a new issue in Paperclip with this information structured clearly

## Issue Format to Create
**Title:** `[SENTRY] {error title} in {environment}`

**Description:**
```
Environment: {production/staging}
Severity: {fatal/error/warning}
First seen: {timestamp}

Error: {error message}

Stack trace (top 10 lines):
{stack trace}

Sentry link: {url to Sentry issue}
```

**Labels:** `bug`, `sentry`, severity level

## Done When
Paperclip issue created. CEO will pick it up on next heartbeat and route it through the full 13-step loop.
```

### Test Procedure
1. Deploy sdlc-spike Django app (Railway, Fly.io, or local ngrok tunnel for testing)
2. Trigger an intentional 500 error (e.g., call an endpoint with bad data)
3. Confirm Sentry catches it
4. Confirm Paperclip routine fires and creates an issue
5. Watch CEO pick it up on next heartbeat

---

## Django pgvector (Conditional)

### When to Add It
Only add pgvector if agents demonstrate a specific limitation that semantic memory would solve. Examples:
- Agent is writing code that duplicates existing code because it can't search the codebase semantically
- Agent is making architecture decisions without awareness of existing patterns
- Agent needs to find similar past issues/solutions

### How to Add It (if needed)
Minimal scope — one Django endpoint:

```
GET /api/memory/search?q={query}&limit=5
```

Returns top-5 semantically similar documents (past issues, code snippets, architecture decisions) from the pgvector store.

Agents call it via the Paperclip `http` adapter — they can make HTTP calls to external APIs.

### What NOT to Build
- No complex Django models
- No full RAG pipeline
- No embedding pipeline beyond what's needed for search
- No authentication layer (internal service only)

---

## Django Spike Cleanup

### Files to Delete
```
core/models.py  →  remove Ticket, Artifact, AgentRun models (keep only what pgvector needs)
core/serializers.py  →  remove Ticket serializer
core/views.py  →  remove Ticket CRUD views
core/tests/test_webhooks.py  →  remove (these tested the wrong architecture)
```

### Files to Keep and Repurpose
```
services/paperclip_client.py  →  keep, this calls Paperclip API (correct direction)
core/views.py (webhook endpoint)  →  repurpose to receive FROM Sentry/Grafana → call paperclip_client
```

### The Correct Webhook Direction
```
WRONG (what we built):   Paperclip → webhook → Django
CORRECT:                 Sentry/Grafana → webhook → Django → Paperclip API
```

Django's webhook endpoint should now:
1. Receive the raw Sentry/Grafana payload
2. Parse it into a Paperclip issue format
3. Call `paperclip_client.create_issue()` (add this method)
4. Return 200

Note: This is only needed if the Paperclip routine skill (above) can't handle the parsing on its own. Try the Paperclip-native approach first.

---

## The Infinite Loop — Final Architecture

```
[Production App]
      ↓ error occurs
[Sentry]
      ↓ webhook
[Paperclip Routine]
      ↓ creates issue
[CEO Agent]
      ↓ decomposes + assigns
[Research → Architect → (Human Gate) → Coder → Tester → Reviewer → Security → (Human Gate)]
      ↓ approved
[Paperclip opens PR]
      ↓ PR merged
[GitHub Actions CI/CD]
      ↓ deploys
[Production App]
      ↓ error occurs (next iteration)
      ↑ loop repeats forever
```

This is the system. Wiganz is the Board of Directors at the two human gates. Everything else runs autonomously.
