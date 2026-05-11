# Phase 1 — Learn Paperclip

> **Read before starting:**
> 1. `docs/superpowers/specs/2026-05-11-paperclip-phase1-spec.md` — what to observe, success criteria
> 2. This file — find the first unchecked `- [ ]`
> 3. `docs/paperclip-learnings/JOURNAL.md` — write entries as you go

**Goal:** Understand how Paperclip actually works by doing. No building. No skills. No pipeline. Just boot it, poke it, and observe.

**Output:** One journal entry that honestly describes what you saw, what surprised you, and what you still don't understand.

---

## Tasks

### Boot

- [ ] Run `npx paperclipai onboard` and complete setup
- [ ] Confirm dashboard loads at `localhost:3100`
- [ ] Explore the dashboard — what sections do you see? What's empty? What's already there?

### Company Setup

- [ ] Create company "MAS-SDLC"
- [ ] Note the company ID — you'll need it for API calls later

### Hire CEO

- [ ] Hire CEO agent with `claude_local` adapter
- [ ] Confirm CEO appears in the org chart
- [ ] Observe: what's the default CEO configuration? Any settings you need to touch?

### Set a Goal

- [ ] Set this company goal: *"Research how to implement user authentication with JWT in a REST API. Produce a short research document summarizing the approach, key libraries, and security considerations."*
- [ ] Watch the CEO's first heartbeat fire
- [ ] Observe: how long does the heartbeat take? What does the CEO produce?

### Watch Decomposition

- [ ] Confirm CEO created sub-issues from the goal
- [ ] Open each sub-issue — what's in it? Title, description, assigned agent?
- [ ] Note: do the sub-issues make sense? Are they atomic and actionable?

### Test Approval Gates

- [ ] Approve one sub-issue — observe what happens next
- [ ] Reject one sub-issue — observe how the CEO responds
- [ ] Note: does rejection produce a new attempt? Does it escalate?

### Watch One Task Execute

- [ ] Hire one Research agent with `claude_local` adapter
- [ ] Assign it the research sub-issue
- [ ] Watch it run — observe the heartbeat logs
- [ ] Read the artifact it produces — is it useful?

### Document

- [ ] Write a journal entry in `docs/paperclip-learnings/JOURNAL.md`
- [ ] Add anything surprising to `docs/paperclip-learnings/gotchas.md`

---

## Definition of Done

- One full CEO heartbeat observed
- One sub-task executed by a worker agent
- One approval gate tested (both approve and reject)
- Journal entry written with honest observations
