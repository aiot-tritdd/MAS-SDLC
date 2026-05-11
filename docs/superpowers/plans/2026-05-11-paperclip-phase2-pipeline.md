# Phase 2 — Build the 13-Step Pipeline

> **Read before starting:**
> 1. `docs/superpowers/specs/2026-05-11-paperclip-phase2-spec.md` — full SKILL.md content for all 6 skills
> 2. This file — find the first unchecked `- [ ]`
> 3. `docs/paperclip-learnings/JOURNAL.md` — Phase 1 findings (important context)

**Prerequisite:** Phase 1 complete. You understand how Paperclip's heartbeat, issues, and approval gates work from real hands-on experience.

**Goal:** Configure the full 13-step autonomous SDLC loop inside Paperclip using skills and agents. No code written. Only Paperclip configured.

**Output:** One real ticket flowing through all 13 steps locally, end-to-end.

---

## Tasks

### Write the 6 Skills

Each skill is a SKILL.md file. Content is in `docs/superpowers/specs/2026-05-11-paperclip-phase2-spec.md`.

- [ ] Write Research skill → save as `skills/research-skill/SKILL.md`
- [ ] Write Architect skill → save as `skills/architect-skill/SKILL.md`
- [ ] Write Coder skill → save as `skills/coder-skill/SKILL.md`
- [ ] Write Tester skill → save as `skills/tester-skill/SKILL.md`
- [ ] Write Reviewer skill → save as `skills/reviewer-skill/SKILL.md`
- [ ] Write Security skill → save as `skills/security-skill/SKILL.md`

### Upload Skills to Paperclip

- [ ] Upload all 6 skills to the MAS-SDLC company in Paperclip
- [ ] Confirm each skill appears in the company skills library
- [ ] Read one loaded skill from an agent's perspective — does it make sense?

### Hire the Agent Team

- [ ] Hire Research agent → load research-skill
- [ ] Hire Architect agent → load architect-skill
- [ ] Hire Coder agent → load coder-skill
- [ ] Hire Tester agent → load tester-skill
- [ ] Hire Reviewer agent → load reviewer-skill
- [ ] Hire Security agent → load security-skill
- [ ] Confirm all 7 agents (CEO + 6) appear in org chart

### Run the Full Loop

- [ ] Create a real ticket: *"Add a /health endpoint to the sdlc-spike Django project that returns `{status: ok}` and HTTP 200"*
- [ ] Watch CEO decompose it into sub-issues for each agent
- [ ] Observe approval gate at Step 4 (after Architect) — review and approve the architecture spec
- [ ] Watch Coder, Tester, Reviewer, Security agents execute in sequence
- [ ] Observe approval gate at Step 10 (after Security) — review and approve before "deploy"
- [ ] Confirm all 13 steps touched

### Document

- [ ] Write a journal entry in `docs/paperclip-learnings/JOURNAL.md`
- [ ] Promote any deep concepts to `docs/paperclip-learnings/concepts/`
- [ ] Add surprises to `docs/paperclip-learnings/gotchas.md`

---

## Definition of Done

- All 6 skills written and uploaded
- All 7 agents hired and configured
- One real ticket ran through all 13 steps locally
- Both approval gates tested (Step 4 + Step 10)
- Journal entry written
