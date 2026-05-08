# How to Think Through All 9 SDLC Phases Yourself
**Purpose:** Learn the REASONING process for every phase — not just the output
**Applies to:** Any new project, not just QuantApp
**When to use:** Whenever you start a new project from scratch

> **FOR HADRIEL (any future session):**
> When Wiganz says "teach me Phase [N] thinking" or "I want to practice this phase myself" →
> Open this guide → ask the questions ONE AT A TIME, Socratically.
> NEVER give the answers directly. Ask guiding questions. Wait for Wiganz to reason through it.
> Only hint after 5+ minutes of being stuck. This is a Socratic teaching document, not a cheat sheet.

---

## The Core Mental Model First

```
Phase 1 = WHAT and WHY         → "What am I building? Why does it exist?"
Phase 2 = HOW it connects      → "How do the pieces talk to each other?"
Phase 3 = WHAT it looks like   → "What does the user see and do?"
Phase 4 = WHERE data lives     → "How is data structured and related?"
Phase 5 = HOW backend works    → "How does the server handle requests?"
Phase 6 = HOW frontend works   → "How does the UI render and interact?"
Phase 7 = DOES it work right   → "What breaks, and when?"
Phase 8 = IS it alive          → "Is it on the internet and stable?"
Phase 9 = IS it staying alive  → "How do I keep it healthy over time?"
```

**The golden rule:** Each phase's output is the INPUT to the next phase.
- Bad Phase 1 → builds the wrong thing in Phase 5
- Bad Phase 4 → rewrites the backend in Phase 5
- Bad Phase 3 → rewrites the frontend in Phase 6

Don't rush phases. A slow Phase 1 saves 10 hours in Phase 6.

---

# PHASE 1 — Ideation & Requirements

## The One Core Question
> *"What problem does this solve, for whom, and what's the minimum needed to solve it?"*

---

## Step 1.1 — Write the Problem Statement

**Question to ask yourself:**
> "If this app didn't exist, what frustrating thing would someone have to do manually?"

**Bad (too vague):** "I want to build a stock tracker."
**Good (specific):** "I want to see all my holdings in one place, know my P&L in real time, and get a signal when a trend turns bearish — without switching between 5 apps."

**How to write it:**
1. Describe the frustration WITHOUT mentioning technology
2. Say WHO feels that frustration
3. Say what relief the app provides

**Test:** Can you explain the problem in one paragraph with zero technical words?

---

## Step 1.2 — Define the Target User

**Question to ask yourself:**
> "Who specifically uses this? What do they know? What do they care about?"

**The trap:** "My user is everyone." → That means you build nothing well.

**Questions to answer about your user:**
- One person or many? → affects whether you need auth
- Technical or not? → affects how complex the UI needs to be
- Mobile or desktop? → affects layout
- How often do they use it? → affects real-time vs. on-demand data needs

---

## Step 1.3 — MoSCoW Feature Prioritization

**What MoSCoW means:**
```
Must Have   → App doesn't work without this
Should Have → Important but not blocking launch
Could Have  → Nice if time allows
Won't Have  → Explicitly out of scope for V1
```

**Question to ask yourself:**
> "If I could only ship 3 features, which 3 make the app actually useful?"

**How to run MoSCoW:**
1. Brain dump EVERY feature idea — no filter
2. For each: "Does the app work without this?" → Yes = Could/Won't. No = Must.
3. Keep Must to 3–5 items MAXIMUM
4. The Won't Have list is as important as the Must Have list — it protects scope

---

## Step 1.4 — Write User Stories

**Format:** "As a [user], I want to [action], so that [benefit]."

**Question to ask yourself:**
> "What are the 5 most important things the user actually DOES in this app?"

**Test:** If any user story contains technical words (API, endpoint, cache, database) → rewrite it. User stories are from the user's perspective, not the engineer's.

---

## Step 1.5 — Define MVP Scope

**Question to ask yourself:**
> "What is the MINIMUM set of features that makes this app genuinely useful?"

**Constraint question:**
> "How many hours do I have? Given that, what can I actually ship?"

**How to lock scope:**
1. List only Must Have features
2. Estimate hours honestly (then multiply by 1.5 — you always underestimate)
3. If total > available hours → move to Won't Have until it fits
4. Write an explicit OUT list — no exceptions, no "just this one thing"

---

## Phase 1 Output Checklist
```
□ Problem statement written (no tech words)
□ User defined specifically (not "everyone")
□ Must Have: 3–5 features only
□ Won't Have: explicit list with reasoning
□ User stories: 4–6 in "As [user], I want [action]..." format
□ Scope constraint: hours estimated, scope fits

If any box is unchecked → don't start Phase 2.
```

---

# PHASE 2 — System Design

## The One Core Question
> *"How do all the parts connect, communicate, and handle data?"*

---

## Step 2.1 — Draw the Architecture Diagram

**Question to ask yourself:**
> "What are the layers of this system and how does data move between them?"

**The 4 standard layers (most web apps):**
```
User → Frontend → Backend → Database
                       ↕
                  External APIs
```

**For each layer, answer:**
- What technology fills this role? (and WHY, not just what)
- What does this layer receive? What does it return?
- What are its responsibilities?

**The delete test:** "If I removed this layer, what breaks?" If nothing breaks → that layer doesn't need to exist.

---

## Step 2.2 — Choose Tech Stack With Reasons

**Question for EACH technology choice:**
> "Why THIS technology and not [the obvious alternative]?"

**Reasoning framework:**
```
1. Do I already know this? → reduces learning curve
2. Is it appropriate for this scale? → don't use Kubernetes for a 1-user app
3. Does it fit my constraints? → 35 hours means simple > powerful
4. Does it solve a specific problem this project has?
```

**The trap:** Choosing tech because it's trendy, not because it solves your problem.

---

## Step 2.3 — Design API Endpoints

**Question to ask yourself:**
> "What questions does the frontend need answered? What actions does it need to trigger?"

**The process:**
1. Look at your user stories from Phase 1
2. For each story: "What data does the UI need to render this?" → becomes a GET endpoint
3. For each user action: "What does the server need to do?" → becomes POST/PUT/DELETE

**REST conventions:**
```
GET    → retrieve data (no side effects)
POST   → create or trigger an action
PUT    → replace a resource entirely
PATCH  → update part of a resource
DELETE → remove a resource
```

**Test:** Read the URL + method aloud. Do you immediately know what it does? If not → rename it.

---

## Step 2.4 — Define the Data Flow

**Question to ask yourself:**
> "If I trace ONE user action from click → database → response, what happens at every step?"

**How to do it:**
- Pick the most complex user action
- Write every single step numbered — from button click to UI update
- For each step: "What if this fails? What does the user see?"

**Why this matters:** Data flow diagrams catch integration bugs before you write one line of code.

---

## Step 2.5 — Identify External Integrations

**Question to ask yourself:**
> "What external systems does my app depend on? What are their limits?"

**For each external dependency:**
- Rate limits? (e.g., Alpha Vantage: 25 calls/day)
- Where do API keys live? (Never in React — always backend environment variables)
- What happens if it's down? (fallback? error message?)
- Cost? (free tier limits)

---

## Phase 2 Output Checklist
```
□ Architecture diagram: layers drawn, tech chosen with reasons
□ Tech stack: every choice has "why this, not that" reasoning
□ API endpoints: method, URL, purpose for each
□ Data flow: one action traced click → DB → response
□ External integrations: identified, constraints documented
□ Deploy targets: where each layer lives in production

If any box is unchecked → don't start Phase 3.
```

---

# PHASE 3 — UI/UX Design

## The One Core Question
> *"What does the user see, and how do they move through the app?"*

---

## Step 3.1 — Map the User Flow

**Question to ask yourself:**
> "What does the user do from the moment they open the app to the moment they've accomplished their goal?"

**How to map it:**
1. Start at "User opens app"
2. List every screen/state they pass through
3. Mark decision points: "Does the data exist? Yes → show it. No → show empty state."
4. End at "User has accomplished [the goal from Phase 1]"

**Test:** Is there any screen the user needs that isn't in this flow? Is there any screen in the flow the user doesn't need?

---

## Step 3.2 — Wireframe (Lo-fi First)

**Question to ask yourself:**
> "If I had to sketch this on paper in 10 minutes, what would each screen look like?"

**What a wireframe needs (and doesn't need):**
- Needs: what goes where (header, sidebar, main content, forms, tables)
- Does NOT need: colors, fonts, pixel-perfect spacing
- Tool: paper, Excalidraw, ASCII art — anything

**The wireframe question:** "If I show this to a non-technical person, can they understand what the app does?"

---

## Step 3.3 — Build the Component Inventory

**Question to ask yourself:**
> "What are the individual building blocks of each screen?"

**How to do it:**
1. Look at your wireframe
2. Circle every distinct UI element: cards, tables, forms, buttons, charts, badges
3. Each circle = one component to build
4. Name each component descriptively: `PortfolioCard`, `HoldingsTable`, `SignalBadge`

**Why this matters:** The component list becomes your Phase 6 build checklist. Every component on the list gets built. Nothing gets missed.

---

## Step 3.4 — Define the Design System

**Question to ask yourself:**
> "What are the visual rules that make everything look consistent?"

**Minimum design system (4 decisions):**
```
1. Colors: background, surface, primary accent, success, error, muted text
2. Typography: one heading font, one body font (max 2 fonts total)
3. Spacing: base unit (4px or 8px) → everything is a multiple of this
4. Borders: border-radius (sharp? rounded? pill?), border color
```

**Test:** Can someone build any new component using only these rules and have it look like it belongs?

---

## Phase 3 Output Checklist
```
□ User flow: start → goal, every screen, every decision point
□ Wireframe: every screen sketched (lo-fi is fine)
□ Component inventory: every UI component named and described
□ Design system: colors, typography, spacing, borders defined as CSS variables

If any box is unchecked → don't start Phase 4.
```

---

# PHASE 4 — Database Design

## The One Core Question
> *"What data do I store, and how is it related?"*

> **This is Wiganz's biggest gap (D-level). Spend the most time here.
> Hadriel: Do NOT skip the reasoning questions. Make Wiganz explain every FK decision.**

---

## Step 4.1 — Identify Entities

**Question to ask yourself:**
> "What are the 'things' in my system that I need to remember?"

**How to find entities:**
1. Go back to your Phase 1 user stories
2. Find all the nouns: "I want to see my **portfolio** P&L on **stocks** I've **traded**"
3. Each meaningful noun = a candidate entity (table)
4. Ask: "Do I need to store data about this?" → Yes = entity. No = just an attribute.

**The attribute vs. entity question:**
- "Is `ticker` an entity?" → No, it's an attribute OF a Stock
- "Is `Transaction` an entity?" → Yes — it has its own data (price, quantity, timestamp)

---

## Step 4.2 — Draw the ER Diagram

**Question to ask yourself:**
> "How does each entity relate to every other entity?"

**The 3 relationship types:**
```
One-to-One  (1:1) → One user has one profile. One stock has one portfolio holding.
One-to-Many (1:N) → One stock has many transactions. One user has many orders.
Many-to-Many(N:M) → One student takes many courses. One course has many students.
```

**Questions to ask for EACH relationship:**
- "Can [A] exist without [B]?" → affects on_delete behavior
- "How many [B]s can one [A] have?" → determines relationship type
- "What happens to [B] if [A] is deleted?" → CASCADE? SET NULL? PROTECT?

**The QuantApp questions (practice these):**
- "Can a Portfolio exist without a Stock?" → No → on_delete=CASCADE
- "Can one Stock have two Portfolio entries?" → No → OneToOne (not ForeignKey)
- "Can one Stock have many Transactions?" → Yes → ForeignKey (1-to-Many)

---

## Step 4.3 — Define Schema Details

**Question to ask yourself for EACH column:**
> "What type is this data? What constraints does it have? Can it be null?"

**Column decisions:**
```
CharField     → text with max length
IntegerField  → whole numbers
DecimalField  → money (use this, never FloatField for money — floating point errors)
DateTimeField → timestamp
BooleanField  → true/false
```

**Constraint questions:**
- "Can this be empty?" → null=True or blank=True
- "Must this be unique across the whole table?" → unique=True
- "Is this auto-generated?" → auto_now / auto_now_add / auto

**The @property vs column question:**
> "Should P&L be stored in the database or computed?"
→ Ask: "If the stock price changes, does my stored P&L become wrong?"
→ Yes → DON'T store it → make it a @property (computed from live data)
→ No → can store it

**Rule:** Never store data that can be derived from other data you already have. It creates inconsistency.

---

## Step 4.4 — Migration Strategy

**Question to ask yourself:**
> "In what ORDER do I create these tables?"

**The dependency rule:**
- Create tables with NO foreign keys first
- Create tables WITH foreign keys after the tables they reference exist
- Stock has no FKs → create first
- Portfolio references Stock → create second
- Transaction references Stock → create second/third

---

## Phase 4 Output Checklist
```
□ All entities identified with reasoning
□ ER diagram: every table, every relationship, cardinality labeled
□ Every relationship type explained: why 1:1 vs 1:N vs N:M
□ Schema: every column with type, constraints, null/not-null
□ Computed properties vs stored columns: decision made and documented
□ Migration order: tables in dependency order

If any box is unchecked → don't write Django models yet.
```

---

# PHASE 5 — Backend Implementation

## The One Core Question
> *"How does the server handle each request, process data, and return a response?"*

---

## Step 5.1 — Project Setup

**Questions to answer before writing code:**
- "What is the folder structure?" → Where do models, serializers, views, URLs live?
- "What are my environment variables?" → Database URL, API keys, secret key
- "How do I connect to the database?" → Django settings.py DATABASES config
- "What packages do I need?" → requirements.txt

**Never hardcode secrets.** API keys and database URLs always go in `.env` files, never in code.

---

## Step 5.2 — For Each Feature: Model → Serializer → ViewSet → URL

**Question to ask yourself at each step:**

**Model:**
> "Does this Django model match the schema I designed in Phase 4 exactly?"

**Serializer:**
> "What data does the frontend actually need? Is there anything it should NOT see?"
- Serializer = the translator between Python objects and JSON
- "Why can't I just send the raw Django model to React?" → Django models aren't JSON. Serializers convert them.
- "What if the frontend needs computed data (like P&L)?" → use `SerializerMethodField`

**ViewSet:**
> "What HTTP methods does this endpoint support? Who should be able to call it?"
- `ModelViewSet` → auto-generates list, create, retrieve, update, destroy
- Custom `@action` → for non-standard operations like "fetch price from Alpha Vantage"
- "Why ViewSet instead of a plain function view?" → ViewSets eliminate boilerplate for standard CRUD

**URL:**
> "Is this URL readable? Does it follow REST conventions?"
- Use DRF Router → auto-generates URLs from ViewSets

**Test after each endpoint:** Open the DRF browsable API or Postman. Does it return what React needs?

---

## Step 5.3 — External API Integration

**Questions to ask yourself:**
- "Where does the API key live?" → Environment variable, never hardcode
- "What happens if the external API is down?" → try/except, return meaningful error
- "Am I caching the result?" → Always cache — don't waste rate-limited calls

---

## Phase 5 Output Checklist (Per Feature Slice)
```
□ Model written and matches Phase 4 schema
□ Migration created and applied
□ Serializer: correct fields, computed fields handled
□ ViewSet: correct HTTP methods, correct router registration
□ URL registered and accessible
□ Tested in Postman/browsable API — returns expected JSON
□ External API calls: key in env var, result cached in DB

If any box is unchecked → don't start Phase 6 for this feature.
```

---

# PHASE 6 — Frontend Implementation

## The One Core Question
> *"How do I turn the design into a working interface that talks to the backend?"*

---

## Step 6.0 — Project Setup (Once, Before Any Feature)

**Questions to answer:**
- "What is my folder structure?" → components/, pages/, hooks/, api/
- "How do I call the backend?" → axios or fetch, base URL in environment variable
- "How do I manage server state?" → TanStack Query (not raw useEffect + fetch)
- "How do I handle routing?" → React Router

---

## Step 6.1 — Build Components From the Inventory

**Question for each component:**
> "What data does this component need? Where does it come from?"

**The 3 component types:**
```
Smart (Container)  → fetches data, manages state, passes to dumb components
Dumb (Presentational) → receives props, just renders, no data fetching
Hybrid             → manages local UI state (open/close, form input) but no API calls
```

**Questions to ask while building:**
- "What are the props this component receives?"
- "What happens when data is loading?" → show skeleton or spinner
- "What happens when data fails?" → show error message
- "What happens when data is empty?" → show empty state (never crash)

---

## Step 6.2 — Connect to the API

**Question to ask yourself:**
> "Which Phase 5 endpoint does this component consume?"

**TanStack Query pattern:**
```javascript
// Instead of: useEffect + fetch + useState(loading) + useState(error)
// Use: one useQuery call that handles all of this automatically

const { data, isLoading, isError } = useQuery({
  queryKey: ['portfolio'],
  queryFn: () => fetch('/api/portfolio/').then(r => r.json())
})
```

**Questions:**
- "What triggers a refetch?" → user action? time interval? button click?
- "After a mutation (POST), which queries need to be invalidated?" → so UI stays fresh

---

## Step 6.3 — Handle All States

**Rule:** Every component that fetches data must handle 3 states:
```
Loading → show spinner or skeleton
Error   → show error message (never a blank white screen)
Success → show the actual data
```

**The 4th state to remember:** Empty data (zero results is different from loading or error).

---

## Step 6.4 — Apply the Design System

**Question to ask yourself:**
> "Am I using the CSS variables from Phase 3's design system, or am I hardcoding colors?"

**Never hardcode:** `color: #e8820a` in a component → always use `color: var(--accent-gold)`
**Why:** When you change the design, you change one variable, not 50 component files.

---

## Phase 6 Output Checklist (Per Feature Slice)
```
□ Component built and matches Phase 3 wireframe
□ Correct component type: smart/dumb/hybrid
□ API connected: correct endpoint, correct HTTP method
□ All 3 states handled: loading, error, success
□ Empty state handled
□ Design system CSS variables used (no hardcoded colors)
□ Tested: does it work end-to-end with real backend data?

If any box is unchecked → don't call this slice "done".
```

---

# PHASE 7 — Testing & QA

## The One Core Question
> *"What breaks, under what conditions, and does the app handle it gracefully?"*

---

## Step 7.1 — Think Like a Chaos Monkey

**Question to ask yourself:**
> "What are all the ways this could fail?"

**Failure categories:**
```
External failures  → Alpha Vantage is down. What does the user see?
Input failures     → User submits empty form. Invalid ticker. Negative quantity.
Edge cases         → Portfolio with zero holdings. Stock with no price yet.
Network failures   → Slow connection. Request timeout.
Data edge cases    → Very large numbers. Decimal precision issues.
```

**For each failure:** "Does the app crash? Return a confusing error? Or handle it gracefully?"

---

## Step 7.2 — Test Each API Endpoint

**Questions for each endpoint:**
- "Does it return the correct data shape?"
- "What does it return if the resource doesn't exist? → 404"
- "What does it return if the input is invalid? → 400"
- "Is it correctly refusing wrong HTTP methods?"

---

## Step 7.3 — Security Check

**Basic security questions:**
- "Are my API keys in environment variables? Not in code?"
- "Is CORS configured? Only allowing my frontend domain?"
- "Does the API accept input without validating it?" → SQL injection, XSS risk
- "Are there any endpoints that should be read-only but accept writes?"

---

## Phase 7 Output Checklist
```
□ Edge cases identified for each feature
□ API endpoints tested: happy path + failure paths
□ Error responses: correct HTTP status codes (200, 400, 404, 500)
□ Frontend: all 3 states tested (loading, error, success)
□ Security: API keys in env vars, CORS configured
□ Manual smoke test: full user flow works end-to-end

If any box is unchecked → don't deploy.
```

---

# PHASE 8 — Deploy & Launch

## The One Core Question
> *"How do I get this running on the internet and keep it running?"*

---

## Step 8.1 — Prepare for Production

**Questions to ask yourself:**
- "What environment variables does each service need?"
- "Is my `DEBUG = False` in Django production settings?"
- "Is my database URL pointing to production DB, not localhost?"
- "Is my React API URL pointing to the Railway backend, not localhost?"

**Environment variable checklist:**
```
Django (Railway):
  SECRET_KEY      → random string, never the dev key
  DATABASE_URL    → auto-provided by Railway
  ALLOWED_HOSTS   → your Railway domain
  ALPHA_VANTAGE_KEY → your API key

React (Vercel):
  VITE_API_URL    → your Railway backend URL
```

---

## Step 8.2 — Deploy Backend (Railway)

**Questions to answer:**
- "Did I push the latest code to GitHub?"
- "Did I run migrations on the production database?"
- "Is the health check endpoint responding?"
- "Can I hit `/api/stocks/` from the browser and get a response?"

---

## Step 8.3 — Deploy Frontend (Vercel)

**Questions to answer:**
- "Does Vercel have the `VITE_API_URL` environment variable set?"
- "Did the build succeed without errors?"
- "Can I open the Vercel URL and see the app?"
- "Does the React app actually call the Railway backend?"

---

## Step 8.4 — End-to-End Test on Production

**The production smoke test:**
1. Open the Vercel URL
2. Can you see the portfolio dashboard?
3. Click "Refresh Price" on one stock — does it update?
4. Record a transaction — does it appear in history?
5. Check the signal panel — does it show Golden/Death Cross?

If all 5 pass → the app is live.

---

## Phase 8 Output Checklist
```
□ All environment variables set in Railway and Vercel
□ Django: DEBUG=False, ALLOWED_HOSTS correct
□ Database migrations run on production
□ Backend health check passes (can hit /api/ in browser)
□ Frontend build succeeded on Vercel
□ End-to-end smoke test: all 5 core actions work on production
□ Live URL documented

If any box is unchecked → not done yet.
```

---

# PHASE 9 — Maintenance & Iteration

## The One Core Question
> *"How do I keep the app healthy and improve it over time?"*

> **Note for QuantApp:** Phase 9 is OUT OF SCOPE for this learning project.
> The cycle ends at a successful Phase 8 deploy.
> But learn the questions — this is what you'll do on every product you ship after.

---

## Step 9.1 — Monitor for Failures

**Questions to set up:**
- "How do I know when the app crashes?" → error tracking (Sentry)
- "How do I know if the API is slow?" → performance monitoring
- "How do I know if users are hitting errors?" → logging

---

## Step 9.2 — Collect Feedback

**Questions to ask:**
- "What do users actually use most?" → analytics
- "What do they struggle with?" → user research
- "What bugs are they hitting?" → bug reports

---

## Step 9.3 — Iterate

**The loop:**
> New feedback → go back to Phase 1 for the new feature → mini-SDLC cycle → ship

This is why Phase 9 connects back to Phase 1. Each iteration gets faster and cleaner.

---

# The Meta-Skill: Universal Questions for Any Project

### Phase 1 Questions (Requirements)
```
□ What problem does this solve? (No tech words)
□ Who specifically uses this? (Not "everyone")
□ What are the 3 features without which the app is useless?
□ What will I NOT build in V1?
□ How many hours do I have? Does scope fit?
```

### Phase 2 Questions (System Design)
```
□ What are the layers? (Frontend, Backend, DB, External APIs)
□ For each layer: what tech and WHY (not just what)?
□ What does the frontend need from the backend? (→ endpoints)
□ Trace one action from click → DB → response. Can you do it?
□ What external dependencies? What are their limits?
```

### Phase 3 Questions (UI/UX)
```
□ What does the user do first when they open the app?
□ What does each screen contain? (wireframe it)
□ What are all the UI components? (name them)
□ What are the visual rules that keep everything consistent?
```

### Phase 4 Questions (Database)
```
□ What are the "things" I need to remember? (entities)
□ How does each entity relate to others? (1:1, 1:N, N:M)
□ What happens to [B] if [A] is deleted? (on_delete)
□ What data should be computed, not stored?
□ In what order do I create the tables? (migration order)
```

### Phase 5 Questions (Backend)
```
□ Does the model match the Phase 4 schema exactly?
□ What does the serializer need to include/exclude?
□ What HTTP methods does this endpoint support?
□ What does it return when the input is invalid?
□ Is the external API key in an environment variable?
```

### Phase 6 Questions (Frontend)
```
□ What data does this component need and where does it come from?
□ Is this a smart, dumb, or hybrid component?
□ What does the user see while loading? On error? When empty?
□ After a mutation, which queries need to be invalidated?
□ Am I using design system variables (not hardcoded colors)?
```

### Phase 7 Questions (Testing)
```
□ What are all the ways this feature could fail?
□ Does the API return correct HTTP status codes on failure?
□ Are API keys in environment variables (never in code)?
□ Does the full user flow work end-to-end?
```

### Phase 8 Questions (Deploy)
```
□ Are all environment variables set in production?
□ Is DEBUG=False?
□ Did migrations run on the production database?
□ Does the production end-to-end smoke test pass?
```

### Phase 9 Questions (Maintenance)
```
□ How do I know when something breaks?
□ How do I collect user feedback?
□ When new feedback arrives, which phase do I go back to?
```

---

# How to Practice This Yourself

**Next time you start ANY new project — before writing code:**

1. Open a blank doc, write "Phase 1"
2. Answer every question from Phase 1 checklist
3. Show to Hadriel → Hadriel asks Socratic questions to stress-test
4. Move to Phase 2, repeat
5. Continue through all phases, producing lightweight docs as you go

**The mastery signal:**
You no longer need this document.
You feel the discomfort of a missing problem statement before you've written it.
You automatically ask "what happens if the external API is down?" before building the integration.
The questions are internal.

That's when this is truly learned.

---

*Guide created 2026-04-15 for Wiganz × QuantApp project.*
*Covers: Phase 1 (Requirements) through Phase 9 (Maintenance)*
*Hadriel instruction: teach one question at a time, Socratically. Never give answers directly.*
