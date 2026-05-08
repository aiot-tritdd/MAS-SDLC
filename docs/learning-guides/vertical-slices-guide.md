# Approach B — Vertical Slices: How Real Production Teams Ship
**Purpose:** Understand the thinking behind feature-complete, end-to-end shipping
**Applies to:** Any project, any team size — this is how great teams build
**When to use:** Before starting any new feature. Before planning any sprint.

> **FOR HADRIEL (any future session):**
> When Wiganz asks "how do I plan my build?" or "what order do I build things?" →
> Reference this guide. Ask the questions Socratically. Don't just hand over the slice plan.
> Make Wiganz reason through what the slices should be and why.

---

## The Core Idea in One Sentence

> Ship one complete, working feature end-to-end before touching the next feature.

That's it. Everything else in this guide is explaining WHY and HOW.

---

## What "Vertical Slice" Means (The Visual)

Imagine your app is a layer cake:

```
┌─────────────────────────────────────────┐
│           FRONTEND (React)              │  ← Layer 3
├─────────────────────────────────────────┤
│           BACKEND (Django API)          │  ← Layer 2
├─────────────────────────────────────────┤
│           DATABASE (PostgreSQL)         │  ← Layer 1
└─────────────────────────────────────────┘
```

**Approach A (Layer by Layer) — the wrong way:**
```
Week 1: Build ALL of Layer 1 (all models, all migrations)
Week 2: Build ALL of Layer 2 (all serializers, all endpoints)
Week 3: Build ALL of Layer 3 (all components)
Week 4: Wire everything together → pray it all works
```

**Approach B (Vertical Slice) — the right way:**
```
Slice 1: Cut through ALL layers for ONE feature
  DB schema for Stocks → Django model → DRF endpoint → React component
  ✅ WORKING: You can see stocks on screen

Slice 2: Cut through ALL layers for the next feature
  DB schema for Portfolio → Django model → DRF endpoint → React component
  ✅ WORKING: You can see portfolio P&L on screen

...and so on
```

The "vertical" in vertical slice = you cut vertically through all layers, not horizontally across one layer.

---

## Why Layer-by-Layer Fails (Approach A Problems)

### Problem 1: Big Bang Integration
```
You build ALL models week 1.
You build ALL endpoints week 2.
You build ALL React components week 3.
Week 4: try to wire it together.

What happens?
→ The endpoint returns data in a shape the component didn't expect
→ The component assumed a field that doesn't exist in the serializer
→ The serializer exposes a field the model doesn't have
→ You spend week 4 debugging integration instead of shipping

With vertical slices: you integrate ONE feature at a time.
Integration bugs surface immediately, not at the end.
```

### Problem 2: Nothing Works Until the End
```
Layer-by-Layer: Nothing is "done" for 3 weeks.
You can't demo anything. You can't test anything real.
You don't know if the app actually works until it's supposed to be finished.

Vertical Slices: After Slice 1, you have a WORKING feature.
You can demo it. You can get feedback. You can test it.
```

### Problem 3: Motivation Dies
```
Building database models for 5 days with nothing to show = demoralizing.
Building the Stocks feature completely and seeing it on screen = 🔥

Real engineers need feedback loops. Vertical slices provide them.
```

---

## Why Vertical Slices is the Production Standard

### Real Teams Ship in Sprints
Agile teams (most professional teams) work in 1–2 week sprints.

At the end of every sprint: **potentially shippable product**.

Not "all the models are done." Not "endpoints are ready."
A **working feature** that a user could use today if needed.

Vertical slices are how you achieve this.

### The "Always Shippable" Principle
Great teams maintain a codebase that could ship at any moment.

```
After Slice 1: "We could ship a basic stock list right now if we had to."
After Slice 2: "We could ship portfolio tracking right now if we had to."
After Slice 4: "We're shipping the full app."
```

This is why companies can respond to market changes fast.
They're not waiting for "everything to be done" — each slice is already done.

### Real Agile Story: The MVP Release
```
Startup scenario:
You planned 6 features for the launch.
Two weeks before launch, the CEO says: "We have to ship in 3 days."

Layer-by-Layer team: "We can't — nothing is fully wired together yet."
Vertical Slice team: "We can ship 3 features right now. The other 3 come next sprint."

Who survives? The vertical slice team.
```

---

## How to Identify Your Vertical Slices

### Step 1: List Your "Must Have" Features (From Phase 1)
These came from your MoSCoW. Each Must Have feature is a candidate slice.

**QuantApp Must Haves:**
- Stock price tracking
- Portfolio P&L
- Transaction history
- Trading signals

→ These become 4 slices.

### Step 2: Order Slices by Dependency

**Question to ask yourself:**
> "Does Slice B need Slice A to exist before it can be built?"

```
Can I build Portfolio without Stock? → NO (Portfolio has FK to Stock)
Can I build Transactions without Stock? → NO (Transaction has FK to Stock)
Can I build Signals without Stock? → NO (Signal is calculated from Stock price)

→ Stock must be Slice 1. Everything depends on it.

Can I build Signals without Portfolio? → YES
Can I build Signals without Transactions? → YES

→ Signals can be Slice 4 (independent of Portfolio and Transactions)
```

**The dependency rule:** Build the thing others depend on first.

### Step 3: Define What "Done" Means for Each Slice

**Question to ask yourself for each slice:**
> "What is the minimum that makes this feature actually work end-to-end?"

**Not done:**
- "The endpoint returns data" → not done if React can't display it
- "The component renders" → not done if it uses hardcoded data instead of real API
- "The model exists" → not done if it's not connected to a working UI

**Done means:**
- DB: table exists with correct schema
- Backend: endpoint returns correct data shape, tested in Postman
- Frontend: component fetches real data from real endpoint, displays correctly
- Edge cases: loading state, error state, empty state all handled
- **You could demo this feature to someone right now**

---

## The Vertical Slice Execution Loop

For EACH slice, follow this exact order:

```
┌─────────────────────────────────────────────────────┐
│  1. DB: Design the schema for this feature only      │
│     (even if you'll add more tables later)           │
└──────────────────────────┬──────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────┐
│  2. Backend: Write model → migration → serializer    │
│     → viewset → URL                                  │
└──────────────────────────┬──────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────┐
│  3. Test: Hit the endpoint in Postman/browsable API  │
│     Does it return the right data shape?             │
│     ✅ YES → move on   ❌ NO → fix before React      │
└──────────────────────────┬──────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────┐
│  4. Frontend: Build the component                    │
│     → connect to real endpoint                       │
│     → handle loading + error + empty states          │
│     → apply design system                            │
└──────────────────────────┬──────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────┐
│  5. End-to-End Test: Does the full feature work?     │
│     Click through it like a real user.               │
│     ✅ YES → SLICE COMPLETE. Mark it done. Celebrate.│
│     ❌ NO  → Fix. Don't move to next slice.          │
└──────────────────────────┬──────────────────────────┘
                           ▼
                   Move to next slice
```

**The most important rule:** Never start the next slice until the current one is fully working.

---

## The "Done" Gate — Don't Cross It Prematurely

This is where discipline separates junior from senior engineers.

**Junior engineer temptation:**
> "The endpoint mostly works. I'll finish the edge cases later and move to the next feature."

**What actually happens:**
> You forget the edge cases.
> The next feature builds on top of the unfinished one.
> The bug compounds.
> By the time you remember, fixing it breaks 3 other things.

**The rule:**
> A feature is either DONE or it's NOT DONE. There is no "mostly done."
> Cross the done gate fully before moving forward.

---

## What Each Slice Teaches You

Beyond just building — each vertical slice teaches a COMPLETE skill set:

```
Slice 1 (Stocks):
→ Learn: How Django model → serializer → viewset pipeline works
→ Learn: How React fetches and displays data from a real API
→ Learn: The full loop from database row to pixels on screen

Slice 2 (Portfolio):
→ Learn: How FK relationships work in practice (Portfolio → Stock)
→ Learn: How computed properties (@property) appear in API responses
→ Learn: How React re-renders when dependent data changes

Slice 3 (Transactions):
→ Learn: How POST endpoints with validation work in DRF
→ Learn: How forms work in React — controlled components
→ Learn: How mutations (POST) trigger cache invalidation in TanStack Query

Slice 4 (Signals):
→ Learn: How complex business logic lives in the API layer (not the DB, not React)
→ Learn: How external API integration works end-to-end
→ Learn: How conditional rendering works in React (Golden vs Death vs Neutral)
```

---

## The Mindset Shift: Features, Not Layers

**Layer thinking (old mindset):**
> "I'm building the database layer today."
> "I'm building the API layer this week."

**Feature thinking (production mindset):**
> "I'm shipping the Stocks feature today."
> "The Portfolio feature is done — moving to Transactions."

The mental unit shifts from **technical layer** to **user value**.
This is how product engineers think. This is how great teams talk.

In a real standup:
- ❌ "I worked on serializers yesterday"
- ✅ "The stock price refresh feature is done and tested"

---

## Vertical Slice Checklist (For Any Feature on Any Project)

**Before starting a slice:**
```
□ I know exactly what "done" looks like for this feature
□ I know which endpoint(s) this feature needs
□ I know which component(s) this feature requires
□ I know if this slice has any dependencies on a previous slice
```

**During the slice:**
```
□ DB schema: designed before writing the model
□ Model: matches the schema, migration applied
□ Serializer: correct fields, tested output shape
□ Endpoint: tested in Postman — happy path AND error paths
□ Component: fetches real data (not hardcoded)
□ States: loading + error + empty all handled
□ Design: uses design system variables
```

**After the slice (the done gate):**
```
□ I can demo this feature to someone right now
□ No broken states (no white screens, no uncaught errors)
□ The next slice can build on this without fear of it breaking
□ I've noted what I learned from this slice
```

---

## Practicing This Yourself

**Next time you plan a project:**

1. List your Must Have features from Phase 1
2. Draw the dependency graph: which features depend on which?
3. Order slices: dependencies first
4. Define "done" for each slice before writing code
5. Execute one slice fully before touching the next
6. At the end of each slice: ask "could I demo this right now?"

**The mastery signal:**
You feel uncomfortable starting a new feature before the current one is fully tested.
You naturally ask "what does done look like?" before writing the first line.
You think in features, not layers.

That's when vertical slices are internalized.

---

*Guide created 2026-04-15 for Wiganz × QuantApp project.*
*Hadriel instruction: when Wiganz plans a new feature or sprint, ask "what's your slice plan?" before any code is written.*
