# Phase 3 — Production Loop

> **Read before starting:**
> 1. `docs/superpowers/specs/2026-05-11-paperclip-phase3-spec.md` — GitHub config, Sentry routine, pgvector scope
> 2. This file — find the first unchecked `- [ ]`
> 3. `docs/paperclip-learnings/JOURNAL.md` — Phase 1 + 2 findings (important context)

**Prerequisite:** Phase 2 complete. The 13-step loop runs locally. You trust what Paperclip does.

**Goal:** Close the infinite loop. Error in production → Sentry → Paperclip auto-ticket → agents fix → PR → GitHub Actions → deploy → monitor → repeat forever.

**Output:** A Sentry error automatically creates a Paperclip issue and the loop starts without human input.

---

## Tasks

### GitHub Integration

- [ ] In Paperclip settings, connect GitHub repository
- [ ] Configure GitHub permissions (what Paperclip needs: repo read/write, PR creation)
- [ ] Test: assign a task to Coder agent → confirm it creates a real branch
- [ ] Test: Coder agent opens a real PR → confirm GitHub Actions CI triggers
- [ ] Observe: what does the PR look like? Does GitHub Actions pass?

### Sentry Routine

- [ ] In Paperclip, create a new routine
- [ ] Configure webhook trigger (signing mode: `hmac_sha256` or `none` for testing)
- [ ] Copy the Paperclip routine webhook URL
- [ ] In Sentry, add the webhook URL as an integration
- [ ] Write the routine skill (content in spec): parse Sentry payload → create Paperclip issue with title, error message, stack trace summary, severity label
- [ ] Test: manually trigger a Sentry alert → confirm Paperclip issue appears automatically
- [ ] Observe: does the CEO pick it up on next heartbeat? Does the full loop kick off?

### Validate the Infinite Loop

- [ ] Trigger a real error in the deployed sdlc-spike Django app
- [ ] Confirm: Sentry catches it → Paperclip routine fires → issue created → CEO decomposes → agents fix → PR opened → GitHub Actions runs → merge → deployed
- [ ] This is the system. Document the full flow in JOURNAL.md.

### Django pgvector (only if gap confirmed)

- [ ] After running Phase 2 and 3, identify: do agents struggle with any task that semantic memory would solve?
- [ ] If yes: add pgvector to Django spike, expose as an API endpoint for agents to call via the `http` adapter
- [ ] If no: leave Django as-is. The spike code stays but pgvector is not built.

### Cleanup Django Spike

- [ ] Delete `core/models/Ticket` — Paperclip IS the ticket system
- [ ] Delete `core/models/Artifact`, `AgentRun` — Paperclip's logs cover this
- [ ] Repurpose webhook endpoints: receive FROM Sentry/Grafana → POST TO Paperclip (not the other way)
- [ ] Keep `services/paperclip_client.py` — Django calling Paperclip API is correct direction

---

## Definition of Done

- Agent opens a real PR on GitHub
- Sentry error auto-creates a Paperclip issue
- Full infinite loop validated end-to-end at least once
- Django spike cleaned up to thin responsibilities only
- Final journal entry written with the full system working
