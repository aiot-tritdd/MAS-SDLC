# QuantApp — Full Product Design Spec
**Date:** 2026-04-15
**Author:** Wiganz + Hadriel (brainstorming session)
**Status:** ✅ Approved — ready for implementation planning

> **FOR ANY FUTURE SESSION (Claude or Hadriel):** Read ALL 4 docs before doing anything:
> 1. This spec — scope, models, UI, SDLC contract, Wiganz's learning profile
> 2. `docs/superpowers/plans/2026-04-15-quant-app-plan.md` — find the first unchecked `- [ ]`
> 3. `docs/learning-guides/sdlc-thinking-guide.md` — Socratic teaching guide for all 9 SDLC phases
> 4. `docs/learning-guides/vertical-slices-guide.md` — vertical slice execution and done gates

---

## TABLE OF CONTENTS

1. Project Identity & Why It Exists
2. Locked Scope (35 hours — non-negotiable)
3. Tech Stack Decision
4. Database Models (3 tables)
5. API Endpoints (5 endpoints)
6. UI Aesthetic — Locked Design Direction
7. Architecture Overview
8. **Approach B — Vertical Slices (The Build Strategy)**
9. **Full SDLC Navigation Plan — All 9 Phases**
10. SDLC × QuantApp Phase Map (Where We Are & Where We're Going)
11. Session Contract (Rules for Every Future Session)
12. Wiganz's Learning Profile
13. Demo Data Reference

---

## 1. Project Identity & Why It Exists

**QuantApp** is a stock portfolio tracker with Golden/Death Cross trading signals.

**This project is NOT primarily about the product.** The product is the vehicle. The real goal is:

> Wiganz goes through a **complete SDLC cycle end-to-end** for the first time,
> building every layer (DB → API → UI) with deep understanding, not copy-paste muscle memory.

### Primary Goal — Learning
- Complete the full Software Development Life Cycle (Phase 1 → Phase 9) for the first time
- Deeply understand **Django REST Framework** — not just use it, but defend it in an interview
- Learn **React** from near-zero through real implementation on a real product
- Master **database schema design** — understand FK, normalization, relationships from scratch
- Experience what a **real production shipping team** process feels like

### Secondary Goal — Portfolio
- A live, deployed project at `railway.app` (backend) + `vercel.app` (frontend)
- Can be demonstrated in interviews as a full-stack, deployed product

### Context — When This Was Decided
- Wiganz is in **Week 5–8 of a 12-week interview prep roadmap**
- This fills the "Tracker Lite project (React + Django)" slot in the roadmap
- 35 total hours budgeted across 4 weeks
- Background: 2–3 years Django/Python experience, React is new territory

---

## 2. Locked Scope (35 Hours — Non-Negotiable)

### What's IN ✅
| Feature | Description |
|---------|-------------|
| Stock price tracking | Fetch from Alpha Vantage API and cache in PostgreSQL |
| Portfolio tracker | Holdings with unrealized P&L calculation |
| Transaction history | Buy/sell records with timestamps |
| Trading signals | Golden Cross / Death Cross (MA50 vs MA200) |
| Dashboard UI | Dark, amber-accented, data-dense single-page dashboard |
| Deployment | Railway (backend + DB) + Vercel (frontend) |

### What's OUT ❌ — PERMANENTLY, NO DISCUSSION
| Feature | Why it's out |
|---------|-------------|
| Authentication / login | Single-user app, adds 10+ hours of scope |
| Multi-user / teams | Requires auth, permissions, data isolation — out of scope |
| Real-time WebSocket feeds | Requires async Django, socket infra — out of scope |
| AI features / predictions | Out of scope for this learning cycle |
| Payment / subscription | Not relevant to this learning goal |
| Mobile app | Separate project entirely |
| Notifications / alerts | Nice to have, not for V1 |

> **Rule:** Any feature not in the IN list requires explicit re-scoping conversation before touching code.
> The 35-hour constraint is REAL. Scope creep kills this project.

---

## 3. Tech Stack Decision (Locked)

| Layer | Technology | Why This Choice |
|-------|-----------|----------------|
| Frontend | **React + Vite** | Industry standard; Wiganz's primary learning target; fast dev server |
| Styling | **TailwindCSS** | Utility-first; builds the dark amber aesthetic fast without custom CSS architecture |
| Charts | **Recharts** | React-native library; simple declarative API; Line + Bar charts for portfolio |
| State / API calls | **TanStack Query (React Query)** | Industry-standard server state management; handles loading/error/cache automatically |
| Backend | **Django + Django REST Framework** | Wiganz's strongest language; DRF is the deep-learning target for this project |
| Database | **PostgreSQL** | Relational; perfect for FK relationships between Stock → Portfolio → Transaction |
| External Data | **Alpha Vantage API (free tier)** | Real stock data; 25 API calls/day limit |
| Backend Deploy | **Railway** | One-command deploy; managed PostgreSQL included; free tier sufficient |
| Frontend Deploy | **Vercel** | One-command deploy; CDN; connects to GitHub for auto-deploy |
| Version Control | **GitHub** | Source of truth; triggers Vercel auto-deploy on push to main |

### Alpha Vantage Constraint — Critical Design Decision
- **25 API calls per day** on free tier
- **Rule:** Django caches every fetched price in PostgreSQL immediately
- **Rule:** React NEVER calls Alpha Vantage directly — all external API calls go through Django
- **Pattern:** On-demand fetch — user clicks "Refresh Price" → Django calls Alpha Vantage → saves to DB → returns updated price to React
- **Why this matters:** This is a real engineering constraint. Designing around rate limits is a production skill.

---

## 4. Database Models (3 Tables)

### The Three Entities

```
┌──────────────┐         ┌──────────────────┐         ┌─────────────────┐
│    STOCK     │         │    PORTFOLIO     │         │   TRANSACTION   │
├──────────────┤         ├──────────────────┤         ├─────────────────┤
│ id (PK)      │◄────────│ id (PK)          │         │ id (PK)         │
│ ticker       │         │ stock (FK)       │    ┌────│ stock (FK)      │
│ name         │◄────────┤ quantity         │    │    │ type (buy/sell) │
│ current_price│         │ avg_buy_price    │    │    │ price           │
│ last_updated │         │ pnl (property*)  │    │    │ quantity        │
└──────────────┘         │ pnl_pct(property*)    │    │ timestamp       │
                         └──────────────────┘    │    └─────────────────┘
                                                 └────► FK to Stock
```

### Full Field Definitions

**Stock**
```python
class Stock(models.Model):
    ticker        = models.CharField(max_length=10, unique=True)  # "AAPL"
    name          = models.CharField(max_length=200)               # "Apple Inc."
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    last_updated  = models.DateTimeField(auto_now=True)
```

**Portfolio**
```python
class Portfolio(models.Model):
    stock         = models.OneToOneField(Stock, on_delete=models.CASCADE)
    quantity      = models.IntegerField()
    avg_buy_price = models.DecimalField(max_digits=10, decimal_places=2)

    # NOT stored in DB — computed Python properties
    @property
    def pnl(self):
        return (self.stock.current_price - self.avg_buy_price) * self.quantity

    @property
    def pnl_percent(self):
        cost_basis = self.avg_buy_price * self.quantity
        return (self.pnl / cost_basis) * 100
```

**Transaction**
```python
class Transaction(models.Model):
    BUY  = 'buy'
    SELL = 'sell'
    TYPE_CHOICES = [(BUY, 'Buy'), (SELL, 'Sell')]

    stock     = models.ForeignKey(Stock, on_delete=models.CASCADE)
    type      = models.CharField(max_length=4, choices=TYPE_CHOICES)
    price     = models.DecimalField(max_digits=10, decimal_places=2)
    quantity  = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

### Relationships Explained
| Relationship | Type | Why |
|---|---|---|
| Portfolio → Stock | OneToOne (FK) | One holding per stock — you either own AAPL or you don't |
| Transaction → Stock | ForeignKey (1-to-many) | One stock can have many buy/sell transactions over time |
| `pnl`, `pnl_percent` | Python `@property` | Computed values — storing them creates data inconsistency when price changes |

---

## 5. API Endpoints (5 Endpoints)

| Method | Endpoint | Purpose | DRF Pattern |
|--------|----------|---------|------------|
| GET | `/api/stocks/` | List all tracked stocks with prices | ModelViewSet — list |
| POST | `/api/stocks/<ticker>/fetch/` | Trigger Alpha Vantage fetch → cache → return price | Custom action `@action` |
| GET | `/api/stocks/<ticker>/signal/` | Calculate MA50 vs MA200 → return signal | Custom action `@action` |
| GET | `/api/portfolio/` | All holdings with live P&L | ModelViewSet — list |
| GET + POST | `/api/transactions/` | List history / record new buy-sell | ModelViewSet — list + create |

### Signal Logic
```python
# MA data fetched from Alpha Vantage daily adjusted endpoint
if MA50 > MA200:
    signal = "Golden Cross"   # 🟢 Bullish — short-term momentum above long-term
    recommendation = "BUY"
elif MA50 < MA200:
    signal = "Death Cross"    # 🔴 Bearish — short-term dropping below long-term
    recommendation = "SELL"
else:
    signal = "Neutral"        # ⚪ No clear trend
    recommendation = "HOLD"
```

### Response Shape Examples
```json
// GET /api/portfolio/
{
  "holdings": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "quantity": 10,
      "avg_buy_price": "150.00",
      "current_price": "185.00",
      "pnl": "350.00",
      "pnl_percent": "23.33",
      "signal": "Golden Cross"
    }
  ],
  "total_value": "24580.00",
  "total_pnl": "4580.00",
  "total_pnl_percent": "22.90"
}
```

---

## 6. UI Aesthetic — Locked Design Direction

### The Fusion
Three visual references were combined into one aesthetic direction:

**1. SOVEREIGN** (from `quant-app-electric-variants.html`)
- Near-black background (#0D0D0D to #111111)
- Gold/amber-colored numbers and accent text
- Clean **Holdings Ledger** table — monospace numbers, tight rows
- **Donut ring** for portfolio P&L with percentage in center
- **Signal Analysis** side panel with MA50/MA200 values
- Gold signal badges: `+ Golden`, `+ Death`, `— Neutral`
- Typography: clean uppercase label tracks (`HOLDINGS LEDGER`, `SIGNAL ANALYSIS`)
- Subtle line chart at bottom of holdings panel

**2. AMBER MACHINE** (from `ui-variants-v4.html`)
- Warm amber (#e8820a) as the primary accent — organic, not cold
- Amber glow effect on key metric numbers (box-shadow glow)
- Circular SVG gauge elements for visual richness
- Split left/right layout energy for certain panels
- Warmth and depth — feels alive, not clinical

**3. VIVID** (from `ui-variants-v4.html`)
- **Gradient glow cards** for top metric panels (portfolio value, daily gain, total P&L)
- Multiple accent colors allowed in small doses: emerald green for gains, red for losses, teal for neutral
- Color-coded portfolio signal dots on holdings rows

### Design Tokens (Locked)
```css
:root {
  /* Backgrounds */
  --bg-primary:   #0D0D0D;   /* Page base — near-black */
  --bg-surface:   #141414;   /* Cards, panels */
  --bg-elevated:  #1a1a1a;   /* Table rows, hover states */
  --bg-border:    #2a2a2a;   /* Dividers, table borders */

  /* Accents */
  --accent-gold:  #e8820a;   /* PRIMARY — amber, warm, organic */
  --accent-green: #22c55e;   /* Positive P&L, Golden Cross */
  --accent-red:   #ef4444;   /* Negative P&L, Death Cross */
  --accent-blue:  #3b82f6;   /* Neutral signal */

  /* Typography */
  --text-primary: #f5f5f5;
  --text-muted:   #6b7280;
  --text-dim:     #4b5563;

  /* Glow effects (AMBER MACHINE influence) */
  --glow-gold:    0 0 20px rgba(232, 130, 10, 0.3);
  --glow-green:   0 0 20px rgba(34, 197, 94, 0.2);
}
```

### UI Component Inventory
| Component | Description | Source Inspiration |
|-----------|-------------|-------------------|
| `PortfolioCard` | Total value + donut P&L ring + unrealized gain | SOVEREIGN donut |
| `HoldingsLedger` | Table: ticker, shares, avg cost, current, P&L, signal badge | SOVEREIGN table |
| `SignalPanel` | MA50, MA200, cross type, recommendation text | SOVEREIGN right panel |
| `MetricStrip` | Daily gain card + total P&L card + best performer card | VIVID gradient glow cards |
| `PriceRefreshButton` | Triggers `/fetch/` — shows loading state | All variants |
| `TransactionForm` | Buy/sell dropdown, ticker, quantity, price | SOVEREIGN form |
| `TransactionHistory` | Scrollable list of past transactions | Standard table |
| `LineChart` | Portfolio value over time (Recharts) | SOVEREIGN bottom chart |
| `SignalBadge` | Small badge: `🟢 Golden`, `🔴 Death`, `⚪ Neutral` | SOVEREIGN badges |

---

## 7. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   USER'S BROWSER                         │
│                                                          │
│  React + Vite                 TanStack Query             │
│  ┌──────────────┐   fetches   ┌──────────────────┐       │
│  │  Dashboard   │────────────▶│  Cache Layer     │       │
│  │  Components  │             │  (auto-refresh,  │       │
│  └──────────────┘             │   loading states)│       │
│                               └────────┬─────────┘       │
└────────────────────────────────────────│─────────────────┘
                                         │ HTTP REST
                                         ▼
┌─────────────────────────────────────────────────────────┐
│               DJANGO REST FRAMEWORK (Railway)            │
│                                                          │
│  ┌────────────┐ ┌─────────────┐ ┌──────────┐ ┌───────┐ │
│  │/api/stocks/│ │/api/stocks/ │ │/api/port-│ │/api/  │ │
│  │            │ │<tkr>/fetch/ │ │folio/    │ │trans- │ │
│  │            │ │<tkr>/signal/│ │          │ │actions│ │
│  └────────────┘ └─────────────┘ └──────────┘ └───────┘ │
│                                                          │
│  Serializers → Viewsets → Models → ORM                  │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
             ▼                          ▼
┌────────────────────┐    ┌─────────────────────────────┐
│   PostgreSQL DB    │    │    Alpha Vantage API         │
│   (Railway)        │    │    (External — 25 calls/day) │
│                    │    │    Called ONLY by Django,    │
│  Stock             │    │    never by React directly   │
│  Portfolio         │    └─────────────────────────────┘
│  Transaction       │
└────────────────────┘
```

### Data Flow (Step by Step)
1. React loads → TanStack Query calls `GET /api/portfolio/`
2. Django queries PostgreSQL → computes P&L from Python properties → returns JSON
3. React renders dashboard (SOVEREIGN/AMBER aesthetic)
4. User clicks "Refresh Price" on AAPL →
5. React calls `POST /api/stocks/AAPL/fetch/`
6. Django hits Alpha Vantage API → saves new price to `Stock.current_price` in DB
7. Django returns updated price → React re-renders
8. Signals: `GET /api/stocks/AAPL/signal/` → Django fetches MA data from Alpha Vantage → returns Golden/Death Cross

---

> 📖 **LEARNING GUIDE — VERTICAL SLICES:**
> `docs/learning-guides/vertical-slices-guide.md`
> Covers: what vertical slices mean, why layer-by-layer fails, how real production teams ship,
> the execution loop, the done gate, and how to identify + order slices on any project.
> Hadriel: when Wiganz starts planning a feature, ask "what's your slice plan?" — guide Socratically.

## 8. Approach B — Vertical Slices (The Build Strategy)

### What "Vertical Slice" Means
A vertical slice is one **complete feature** built **end-to-end** before moving to the next feature.

**NOT this (Layer by layer — Approach A):**
```
Week 1: Write ALL Django models
Week 2: Write ALL DRF serializers + endpoints
Week 3: Write ALL React components
Week 4: Wire everything together → pray it works
```
Problem: Big-bang integration. Nothing works until Week 4. Hard to debug. Hard to validate.

**YES this (Vertical Slice — Approach B):**
```
Feature 1 (Stocks):
  → DB schema for Stock table
  → Django model + migration
  → DRF serializer + viewset + URL
  → Test API in Postman ✅
  → React component that lists stocks
  → Stocks feature DONE and WORKING ✅

Feature 2 (Portfolio):
  → DB schema for Portfolio table + FK to Stock
  → Django model + P&L property
  → DRF serializer (with computed fields)
  → Test API ✅
  → React Portfolio card + Holdings table
  → Portfolio feature DONE and WORKING ✅

... and so on
```

### Why This is the Production/Enterprise Way
- You have a **working, shippable product after every feature** — not just at the end
- Integration issues are caught **early** (within each slice) not late (all at once)
- Easy to **demo progress** — "here's the working stocks feature"
- Mirrors how **real agile teams** work — sprint by sprint, feature by feature
- Each vertical slice is its own **complete SDLC mini-cycle**: design → build → test → done

### The 4 Vertical Slices for QuantApp

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE ZERO: DB Schema Design (SDLC Phase 4)                    │
│  Design ALL tables + relationships before writing any code       │
│  Output: ER diagram + schema definition doc                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │ (schema locked, then build begins)
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  SLICE 1: Stocks Feature                                          │
│  ├── SDLC Phase 5 (Backend): Stock model + migration             │
│  │    + StockSerializer + StockViewSet + /api/stocks/ route      │
│  │    + /fetch/ custom action (Alpha Vantage integration)        │
│  ├── SDLC Phase 6 (Frontend): StockList component + fetch button │
│  └── ✅ WORKING: Can see stocks, can refresh prices              │
└──────────────────────────────┬───────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  SLICE 2: Portfolio Feature                                       │
│  ├── SDLC Phase 5: Portfolio model + pnl/pnl_percent properties  │
│  │    + PortfolioSerializer + /api/portfolio/ endpoint           │
│  ├── SDLC Phase 6: PortfolioCard + HoldingsLedger table          │
│  └── ✅ WORKING: Can see holdings with real P&L numbers          │
└──────────────────────────────┬───────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  SLICE 3: Transactions Feature                                    │
│  ├── SDLC Phase 5: Transaction model + GET + POST endpoints      │
│  ├── SDLC Phase 6: TransactionHistory list + buy/sell form       │
│  └── ✅ WORKING: Can record and view all trades                  │
└──────────────────────────────┬───────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  SLICE 4: Signals Feature                                         │
│  ├── SDLC Phase 5: MA50/MA200 calculation + /signal/ endpoint    │
│  ├── SDLC Phase 6: SignalBadge on table + SignalPanel             │
│  └── ✅ WORKING: Golden/Death Cross visible on every holding     │
└──────────────────────────────┬───────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE FINAL: Deploy (SDLC Phase 8)                              │
│  ├── Railway: Django + PostgreSQL                                 │
│  ├── Vercel: React                                                │
│  └── ✅ LIVE: Real URL, shareable, portfolio-ready               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 9. Full SDLC Navigation Plan — All 9 Phases

> This is the process map for the entire project.
> Every future session MUST reference this to know where we are and what's next.
> At the start of each phase: call the phase banner, produce the lightweight doc, follow the checklist.

---

> 📖 **LEARNING GUIDE — ALL 9 PHASES:**
> `docs/learning-guides/sdlc-thinking-guide.md`
> Wiganz wants to learn HOW to think through EVERY SDLC phase themselves.
> This guide covers Phase 1 through Phase 9: the thinking process, questions to ask,
> reasoning frameworks, and output checklists for each phase.
> When starting a new project OR when Wiganz says "teach me Phase [N] thinking" →
> Hadriel opens that guide → finds that phase → asks the questions ONE AT A TIME, Socratically.
> NEVER give answers directly. Let Wiganz reason through each question first.

### 📋 PHASE 1 — Ideation & Requirements
**Status: ✅ COMPLETE**
**SDLC Duration:** 2–3 days | **QuantApp:** 1 session (this brainstorming session)

**What we did:**
- Defined the problem, users, goals (Section 1 of this spec)
- Locked the MoSCoW feature list (Section 2)
- Established learning goals and success criteria
- Confirmed tech stack (Section 3)

**Lightweight doc produced:** This spec document (`2026-04-15-quant-app-design.md`) serves as the PRD.

**SDLC Checklist for QuantApp:**
- [x] Problem statement defined
- [x] Target user identified (Wiganz — solo, single-user)
- [x] MoSCoW features locked (Section 2)
- [x] User stories: "As Wiganz, I want to see my portfolio P&L, so I know if I'm making money"
- [x] MVP scope: 4 features, no auth, 35 hours

---

### 🏗️ PHASE 2 — System Design
**Status: ✅ COMPLETE**
**SDLC Duration:** 2–4 days | **QuantApp:** 1 session (this brainstorming session)

**What we did:**
- Defined architecture diagram (Section 7)
- Chose tech stack with reasoning (Section 3)
- Defined all 5 API endpoints + response shapes (Section 5)
- Defined data flow (Section 7)
- Identified integration points (Alpha Vantage — 25 calls/day constraint)

**Lightweight doc produced:** This spec (Sections 3, 5, 7 cover architecture, API spec, data flow).

**SDLC Checklist for QuantApp:**
- [x] Architecture diagram (React → Django → PostgreSQL → Alpha Vantage)
- [x] Tech stack decision with reasoning
- [x] API endpoints defined (5 endpoints, methods, purposes)
- [x] Data flow documented
- [x] Alpha Vantage integration constraint documented

---

### 🎨 PHASE 3 — UI/UX Design
**Status: ✅ COMPLETE**
**SDLC Duration:** 3–5 days | **QuantApp:** Multiple sessions of visual exploration

**What we did:**
- Explored 20+ UI variants across 4 rounds of iteration
- Round 1: AURORA, SIGNAL, HOLOGRAPHIC, BLUEPRINT, SOLAR
- Round 2: OBSIDIAN, CARBON, NEON BLADE, EMBER, PULSE
- Round 3: DYNASTY, INK WASH, CELESTIAL, GARDEN, TEMPEST (Fantasy Art × Fintech)
- Round 4: NEXUS, INFERNO, AMBER MACHINE, CANOPY, VIVID
- Final selection: **SOVEREIGN + AMBER MACHINE + VIVID fusion** (Section 6)
- Defined design tokens, component inventory (Section 6)

**Lightweight doc produced:** Section 6 of this spec covers UI design system, color tokens, component inventory.

**SDLC Checklist for QuantApp:**
- [x] User flow: open app → see portfolio dashboard → check signals → refresh prices → record transaction
- [x] Visual direction: SOVEREIGN + AMBER MACHINE + VIVID (near-black, warm amber, gradient glow)
- [x] Design tokens locked (CSS variables in Section 6)
- [x] Component inventory defined (8 components in Section 6)
- [ ] Hi-fi mockup: to be built as the first React step (Phase 6 Step 0 — static HTML shell)

---

### 🗄️ PHASE 4 — Database Design
**Status: ⏳ PENDING — First active step when building starts**
**SDLC Duration:** 1–2 days | **QuantApp:** 1 focused session

**What we'll do:**
- Deep-dive on WHY each table exists and WHY each FK is there
- Draw the ER diagram together (Wiganz draws, Hadriel guides via Socratic questions)
- Understand normalization: why `pnl` is a computed property and NOT a stored column
- Understand the difference between OneToOne (Portfolio→Stock) vs ForeignKey (Transaction→Stock)
- Write the Django models only AFTER the schema is fully understood

**Lightweight doc to produce:**
- `docs/db/er-diagram.md` — ER diagram in ASCII/Mermaid + relationship explanations
- `docs/db/schema.md` — Full schema: table, columns, types, constraints, indexes

**SDLC Checklist for QuantApp Phase 4:**
- [ ] Identify all entities: Stock, Portfolio, Transaction
- [ ] Draw ER diagram — relationships and cardinalities
- [ ] Understand WHY OneToOne for Portfolio (can't hold same stock twice)
- [ ] Understand WHY ForeignKey for Transaction (many transactions per stock)
- [ ] Understand WHY pnl is @property not a column (computed from live price)
- [ ] Schema definition: all columns, types, constraints
- [ ] Django migrations plan: Stock first (no FKs), then Portfolio, then Transaction

**Phase Banner to use at start:**
```
╔══════════════════════════════════════════════════════╗
║  🗄️  SDLC — Phase 4: Database Design                ║
║  Goal: Understand schema BEFORE writing any code     ║
║  Output: ER diagram + schema.md                      ║
╚══════════════════════════════════════════════════════╝
```

---

### ⚙️ PHASE 5 — Backend Implementation (Per Vertical Slice)
**Status: ⏳ PENDING**
**SDLC Duration:** 1–2 weeks | **QuantApp:** ~15 hours across 4 slices

**What we'll do (per slice):**
- For each feature slice: model → migration → serializer → viewset → URL → test
- Deep-dive on DRF concepts AT THE MOMENT they appear:
  - "What does a Serializer actually do?" (when we write the first one)
  - "Why does ViewSet exist instead of plain views?" (when we write the first one)
  - "What is `on_delete=CASCADE` actually doing?" (when we write FK)
- Test each endpoint in Postman/DRF browsable API before moving to React

**Lightweight doc to produce:**
- `docs/api/api-spec.md` — All 5 endpoints with request/response examples
- DRF auto-generates `/api/schema/` — use that as live API doc

**Phase Banner to use at start of each slice backend step:**
```
╔══════════════════════════════════════════════════════╗
║  ⚙️  SDLC — Phase 5: Backend (Slice: [Feature Name]) ║
║  Goal: Model + Serializer + Viewset + Test           ║
╚══════════════════════════════════════════════════════╝
```

---

### ⚛️ PHASE 6 — Frontend Implementation (Per Vertical Slice)
**Status: ⏳ PENDING**
**SDLC Duration:** 1–2 weeks | **QuantApp:** ~12 hours across 4 slices

**What we'll do (per slice):**
- Phase 6 Step 0 (once, before slices): Set up React + Vite + TailwindCSS + project structure
- For each feature slice: component → connect to API → handle loading/error states → style
- Deep-dive on React concepts AT THE MOMENT they appear:
  - "What is useState actually storing?" (when we write the first stateful component)
  - "Why does useEffect run twice in dev mode?" (when we see it happen)
  - "What is TanStack Query doing that useEffect + fetch wasn't?" (when we migrate)
- Follow SOVEREIGN + AMBER MACHINE + VIVID aesthetic — design tokens from Section 6

**Lightweight doc to produce:**
- `docs/frontend/components.md` — All 8 components: props, purpose, which API it calls

**Phase Banner to use:**
```
╔══════════════════════════════════════════════════════╗
║  ⚛️  SDLC — Phase 6: Frontend (Slice: [Feature Name])║
║  Goal: Component → API wired → styled → working      ║
╚══════════════════════════════════════════════════════╝
```

---

### 🧪 PHASE 7 — Testing & QA
**Status: ⏳ PENDING — Lightweight for this learning project**
**SDLC Duration:** 3–5 days | **QuantApp:** ~4 hours (lightweight)

**What we'll do:**
- API testing: Postman collection for all 5 endpoints (already done during Phase 5 per slice)
- Edge cases to test: What if Alpha Vantage is down? What if ticker doesn't exist? Empty portfolio?
- Basic DRF test for one endpoint (to learn the pattern — not full coverage)
- Frontend: smoke test all pages render without errors
- Security: CORS config correct, API not publicly writable

**Lightweight doc to produce:**
- `docs/testing/test-plan.md` — Key test cases per feature

**Phase Banner:**
```
╔══════════════════════════════════════════════════════╗
║  🧪 SDLC — Phase 7: Testing & QA                    ║
║  Goal: Edge cases, API tests, basic security check   ║
╚══════════════════════════════════════════════════════╝
```

---

### 🚀 PHASE 8 — Deploy & Launch
**Status: ⏳ PENDING**
**SDLC Duration:** 2–3 days | **QuantApp:** ~3 hours (fast lane — D priority)

**What we'll do:**
- Railway: deploy Django + PostgreSQL, set env vars, run migrations on Railway
- Vercel: deploy React, set `VITE_API_URL` env var pointing to Railway URL
- Test the full deployed app end-to-end with real Alpha Vantage calls
- Share live URL

**Lightweight doc to produce:**
- `docs/deploy/deploy-guide.md` — Step-by-step Railway + Vercel deployment
- `docs/deploy/env-config.md` — All required environment variables

**Phase Banner:**
```
╔══════════════════════════════════════════════════════╗
║  🚀 SDLC — Phase 8: Deploy & Launch                 ║
║  Goal: Live app at Railway + Vercel URLs             ║
╚══════════════════════════════════════════════════════╝
```

---

### 🔁 PHASE 9 — Maintenance & Iteration
**Status: OUT OF SCOPE for this project**

Phase 9 (monitoring, changelog, post-mortems, feature iteration) is out of scope for this learning project. The cycle ends at a successful Phase 8 deploy. Phase 9 is the domain of ongoing products with real users — that's a future project.

---

## 10. SDLC × QuantApp Phase Map (Current Status)

```
Phase 1 — Requirements    ✅ COMPLETE  (this spec is the output)
Phase 2 — System Design   ✅ COMPLETE  (this spec covers architecture + APIs)
Phase 3 — UI/UX Design    ✅ COMPLETE  (Section 6 + 4 rounds of visual exploration)
Phase 4 — DB Design       ⏳ NEXT      (first session of actual building)
Phase 5 — Backend         ⏳ PENDING   (per-slice: Stock, Portfolio, Transaction, Signal)
Phase 6 — Frontend        ⏳ PENDING   (per-slice, paired with Phase 5)
Phase 7 — Testing         ⏳ PENDING   (lightweight — after all slices done)
Phase 8 — Deploy          ⏳ PENDING   (Railway + Vercel at the end)
Phase 9 — Maintenance     ❌ OUT OF SCOPE
```

**When a new implementation session starts:**
1. Look at this map → identify current phase
2. Call the phase banner at the top of the session
3. Follow the checklist for that phase
4. Produce the lightweight doc for that phase before moving to the next

---

## 11. Session Contract (Rules for Every Future Session)

These rules apply to EVERY Claude/Hadriel session that works on QuantApp:

### Navigation Rules
1. **Start every session** by reading this spec → identifying current phase → calling the phase banner
2. **Phase banner** must be displayed whenever entering a new SDLC phase
3. **Never skip a phase** — the whole point is going through every phase at least once
4. **Produce the lightweight doc** for each phase before moving to the next

### Teaching Rules (Hadriel's Approach)
5. **Wiganz writes the code** — Hadriel never writes production code for Wiganz
6. **Socratic method** — guide via questions, never give direct answers
7. **Explain every DRF concept** when it first appears (serializer, viewset, router, etc.)
8. **Explain every DB concept** when it first appears (FK, CASCADE, migration, property vs column)
9. **Explain every React concept** when it first appears (useState, useEffect, component lifecycle)
10. **If Wiganz doesn't understand** → find a different explanation. NEVER say "just trust it"

### Code Rules
11. **Vertical slices** — one feature completely done (DB → API → UI → tested) before the next
12. **No scope creep** — if a feature isn't in Section 2's IN list, flag it and discuss
13. **Alpha Vantage constraint** — Django caches everything, React never calls Alpha Vantage directly
14. **Test each API endpoint** in Postman/browsable API before wiring React

### Progress Tracking
15. **Update `memory/coding-progress.json`** after each session with what was built
16. **Check off SDLC checklist items** as they're completed
17. **Note aha moments** — the moments Wiganz understands WHY something works

---

## 12. Wiganz's Learning Profile (Calibration for Implementation Sessions)

| Area | Current Level | How to Calibrate |
|------|-------------|-----------------|
| React | C/D — copy-paste, can't explain data flow | Slow down here. Explain component lifecycle, hooks, and data flow from first principles. Use metaphors. |
| DRF | B — uses it daily, can't explain/defend internals | Focus on the WHY behind serializers and viewsets. "What would happen if we didn't have serializers?" |
| DB Design | D — complete magic cloud, can't design schema on own | This is the biggest gap. Spend most time in Phase 4. Use ER diagrams. Ask guiding questions: "What happens to a Portfolio if its Stock is deleted?" |
| Python/Django | Expert | Move fast here. Don't over-explain Django basics. |
| Deployment | Beginner | Follow the deploy guide. Explain env vars and why they exist. Keep it practical. |
| JavaScript | Good | Can handle modern JS. Don't over-explain JS syntax. |

### Learning Goals by End of Project
- **React:** Can explain useState/useEffect, component lifecycle, and why TanStack Query replaces naive useEffect + fetch
- **DRF:** Can explain serializers, viewsets, routers, and custom actions to another developer — not just use them
- **DB:** Can design a relational schema from scratch, explain FK vs OneToOne, explain why computed properties don't go in the DB

---

## 13. Demo Data Reference (For UI Development)

Use this data consistently across all UI components and mockups:

```
PORTFOLIO SUMMARY
─────────────────────────────────────
Total Value:    $24,580
Unrealized P&L: +$4,580  (+22.9%)
Daily Gain:     +$847
Best Performer: MSFT +65.8%

HOLDINGS LEDGER
──────────────────────────────────────────────────────
Symbol  Shares  Avg Cost  Current  P&L       Signal
──────────────────────────────────────────────────────
AAPL    10      $150.00   $185.00  +$350     🟢 Golden
NVDA     5      $380.00   $576.00  +$980     🟢 Golden
TSLA     8      $240.00   $217.50  -$180     🔴 Death
MSFT     4      $380.00   $630.00  +$1,000   ⚪ Neutral

SIGNAL ANALYSIS (AAPL example)
─────────────────────────────
Current Price:  $185.40
MA 50-Day:      $182.30
MA 200-Day:     $178.20
Today's Gain:   +$423
Best Performer: MSFT +65.8%
Portfolio Signal: 🟢 Bullish
```

---

*Spec written 2026-04-15. All sections approved by Wiganz before implementation begins.*
*Implementation begins at SDLC Phase 4 — Database Design.*
