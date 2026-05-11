# Phase 1 Spec — Learn Paperclip

**Date:** 2026-05-11
**Status:** Active
**Paired plan:** `docs/superpowers/plans/2026-05-11-paperclip-phase1-learn.md`

---

## What Phase 1 Produces

Not code. Not a pipeline. **Understanding.**

By end of Phase 1, you should be able to answer these from memory:
- What does a Paperclip heartbeat cycle look like step by step?
- How does the CEO decompose a goal into sub-issues?
- What does "approval gate" look like in the dashboard — where is it, what do you click?
- What does a completed agent task produce? What artifact format?
- What does rejection do — does the CEO retry, escalate, or stop?

---

## What to Observe at Each Step

### CEO First Heartbeat
- Does it read the company goal immediately or wait for next cycle?
- What does the heartbeat log show? How many steps visible?
- How long between heartbeat cycles? (default: configurable in settings)

### Sub-issue Structure
A Paperclip sub-issue should have:
- Clear title derived from the goal
- Description with enough context for the assigned agent
- Status: `todo` (waiting to be picked up)
- Parent issue reference linking back to the top-level goal

If sub-issues are vague or missing context — that's a skill problem (Phase 2). Note it in the journal.

### Approval Gate in Dashboard
Location: inside the issue detail view. Look for a "Request Approval" or pending approval status.
What you should see:
- The issue paused at `in_review`
- A prompt to approve or reject with optional feedback
- On approval: issue moves forward
- On rejection: issue returns to `todo` with your feedback attached

### Completed Task Artifact
After a Research agent runs, it should produce a document attached to the issue. Look for:
- A markdown document in the issue's documents tab
- Content: research summary, sources, key findings
- Quality check: is it actually useful or generic filler?

---

## Success Criteria

| Criterion | Pass |
|---|---|
| Paperclip boots cleanly | Dashboard at `localhost:3100` with no errors |
| CEO hired | Appears in org chart, heartbeat configured |
| Goal set | CEO picks it up within one heartbeat cycle |
| Sub-issues created | At least 2 sub-issues, each with clear title + description |
| Approval gate tested | Both approve and reject flows observed |
| Worker agent completes task | Artifact produced and attached to issue |
| Journal written | Honest entry with at least one surprise and one open question |

---

## Notes from Source Code

From deep analysis of `server/src/services/heartbeat.ts`:
- Heartbeat is a 9-step protocol: identity check → goal review → approval follow-up → assignment check → checkout → work → delegate → update → exit
- CEO runs on the same heartbeat as worker agents — same protocol, different role
- Issues use checkout/locking — only one agent can work on an issue at a time

From `server/src/services/issues.ts` (4193 lines):
- Issue status flow: `backlog` → `todo` → `in_progress` → `in_review` → `done`
- Sub-issues are full issues with a `parentId` reference
- Approval gates are built into the `in_review` → `done` transition

These are facts from the source. Phase 1 is about feeling them in practice.
