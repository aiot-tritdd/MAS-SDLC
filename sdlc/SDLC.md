# Software Development Life Cycle (SDLC) Reference

> **Context:** This document was derived from a discussion about going from idea to production as a solo developer.
> **Core diagnosis:** Not lacking coding skill — lacking a systematic process (never completed a full cycle end-to-end).
> **Keyword:** SDLC (Software Development Life Cycle)
> **Visual roadmap:** See `sdlc-roadmap.html` for the interactive version.
> **Discussion log:** See `claude-discuss-session.md` for the full analysis.

---

## Overview

```
Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9
  ↑                                         |
  └─────────── (new feature / feedback) ─────┘
```

This is a **cycle**, not a straight line. After Phase 9, new features/feedback loop back to Phase 1. Each iteration gets faster and cleaner.

**Golden Rule:** Don't aim for perfection each phase. Aim to **go through every phase at least once**. First time will be messy. That's normal.

| Phase | Name | Duration (Solo) |
|-------|------|-----------------|
| 1 | Ideation & Requirements | 2-3 days |
| 2 | System Design | 2-4 days |
| 3 | UI/UX Design | 3-5 days |
| 4 | Database Design | 1-2 days |
| 5 | Backend Implementation | 1-2 weeks |
| 6 | Frontend Implementation | 1-2 weeks |
| 7 | Testing & QA | 3-5 days |
| 8 | Deploy & Launch | 2-3 days |
| 9 | Maintenance & Iteration | Ongoing |

**Total MVP timeline:** ~4-6 weeks + ongoing maintenance

---

## Phase 1: Ideation & Requirements

**Purpose:** Transform a vague idea into concrete, actionable requirements. This is the phase most solo developers SKIP — and exactly why they freeze when projects get complex.

**Key question:** *"What am I building, for whom, solving what problem?"*

### Checklist

1. **Problem Statement** — What problem does this app solve?
2. **Target Users** — Who uses it? (yourself? others?) This affects every decision downstream.
3. **Core Features (MoSCoW)** — Must / Should / Could / Won't have. Keep Must to 3-5 items max.
4. **User Stories** — Format: "As a [role], I want [action], so that [benefit]"
5. **MVP Scope** — Only 2-3 core features. Do NOT build everything. Solo devs die here.

### Skills Needed

| Skill | Why |
|-------|-----|
| Product Thinking | Understand what to build and why |
| Problem Decomposition | Break big ideas into small, buildable pieces |

### Tools

- **Notion** — Requirements docs, feature lists
- **Excalidraw** — Quick sketches, brainstorming
- **Linear** — Task/issue tracking

### Documentation Output (3 docs)

| Document | Description |
|----------|-------------|
| **PRD (Product Requirements Document)** | Product description: problem, users, features, MVP scope, success metrics |
| **User Stories Document** | List of user stories: "As [role], I want [action], so that [benefit]" |
| **MoSCoW Feature List** | Feature classification table: Must / Should / Could / Won't have |

---

## Phase 2: System Design

**Purpose:** Draw the blueprint — how FE, BE, DB, and external APIs connect. Like an architecture plan before building a house.

**Key question:** *"What does the system look like and how do parts communicate?"*

### Checklist

1. **Architecture Diagram** — User -> FE -> BE -> DB -> External APIs
2. **Choose Tech Stack** — Language, framework, hosting for each component
3. **API Design** — Endpoints, methods, request/response formats
4. **Data Flow** — How data moves through the system
5. **Integration Points** — External APIs, third-party services. Keep it simple for V1.

### Skills Needed

| Skill | Why |
|-------|-----|
| System Design basics | Understand how components fit together |
| API Design | Define clean contracts between FE and BE |
| Data Modeling | Know how data flows and gets stored |

### Tools

- **Excalidraw** — Architecture diagrams
- **dbdiagram.io** — Quick DB schema visualization
- **Swagger / OpenAPI** — API specification

### Documentation Output (4 docs)

| Document | Description |
|----------|-------------|
| **Architecture Diagram** | Overall diagram: FE, BE, DB, external APIs, how they connect |
| **Tech Stack Decision Record** | Why each technology was chosen + alternatives considered |
| **API Specification (OpenAPI/Swagger)** | Endpoints, methods, request/response format, auth |
| **Data Flow Diagram** | Where data comes from -> where it goes -> through which services |

---

## Phase 3: UI/UX Design

**Purpose:** Design layout, components, and user flow BEFORE coding. Skipping this = messy frontend, constant refactoring.

**Key question:** *"What does the app look like and how does the user navigate it?"*

### Checklist

1. **User Flow** — Map the journey: Login -> Dashboard -> Detail -> Action -> Result
2. **Wireframe (Lo-fi)** — Sketch on paper or Excalidraw. Doesn't need to be pretty — just show what goes where.
3. **Component List** — Every UI component needed (cards, forms, tables, nav...)
4. **Design System** — 2-3 main colors, 1 heading font, 1 body font, spacing grid
5. **Mockup (optional)** — Higher fidelity in Figma or AI-generated prototypes

### Skills Needed

| Skill | Why |
|-------|-----|
| Basic UI/UX | Understand user-centered design principles |
| Wireframing | Translate ideas into visual layouts quickly |
| Design Systems | Create consistent visual language |

### Tools

- **Figma** — Design mockups and prototypes
- **Excalidraw** — Quick wireframes
- **Coolors.co** — Color palette generation

### Documentation Output (4 docs)

| Document | Description |
|----------|-------------|
| **User Flow Diagram** | Steps the user takes from opening app -> completing their goal |
| **Wireframes (Lo-fi & Hi-fi)** | Layout sketches per page: header, sidebar, main content placement |
| **Component Inventory** | List of all UI components to build + functional description |
| **Design System / Style Guide** | Colors, typography, spacing, border-radius, shadows — all visual rules |

---

## Phase 4: Database Design

**Purpose:** Design tables, columns, and relationships. Good schema = easy backend code. Bad schema = pain forever. Do this BEFORE coding the backend.

**Key question:** *"What data do I store and how is it related?"*

### Checklist

1. **Entities** — Identify all data objects (User, Product, Order, etc.)
2. **ER Diagram** — Map relationships: 1-to-1, 1-to-many, many-to-many
3. **Schema Details** — Columns, data types, constraints, indexes per table
4. **Migration Strategy** — Version control for DB changes (e.g., Alembic, Prisma Migrate)

### Skills Needed

| Skill | Why |
|-------|-----|
| Database Design | Structure data correctly from the start |
| SQL | Query and manipulate relational data |
| Normalization | Avoid redundancy, maintain data integrity |

### Tools

- **dbdiagram.io** — Visual schema design
- **DBeaver** — Database management GUI
- **Alembic / Prisma Migrate** — DB migration management

### Documentation Output (3 docs)

| Document | Description |
|----------|-------------|
| **ER Diagram** | Entity relationship diagram: 1-1, 1-N, N-N relationships |
| **Schema Definition** | Detailed per-table: columns, data types, constraints, indexes |
| **Migration Plan** | Table creation order, seed data, rollback strategy |

---

## Phase 5: Backend Implementation

**Purpose:** Build APIs, business logic, data pipelines. This is where the core functionality lives.

**Key question:** *"How does the server handle requests and process data?"*

### Checklist

1. **Project Setup** — Init framework, folder structure, env config, DB connection
2. **CRUD APIs** — Core endpoints for each entity
3. **External Integrations** — Third-party API connections
4. **Business Logic / Pipelines** — Core processing (ML, calculations, etc.)
5. **Testing** — Unit tests + integration tests

### Skills Needed

| Skill | Why |
|-------|-----|
| Python (or chosen BE language) | Write server-side code |
| REST API | Build clean, predictable endpoints |
| ML basics (if applicable) | Build prediction/processing pipelines |
| Testing | Ensure code works correctly |

### Tools

- **FastAPI / Express / Django** — Web framework
- **SQLAlchemy / Prisma** — ORM
- **pytest / Jest** — Testing
- **Docker** — Containerization

### Documentation Output (4 docs)

| Document | Description |
|----------|-------------|
| **README.md** | Setup guide: how to install, run locally, required env variables |
| **API Documentation (auto-gen)** | Auto-generated docs (e.g., FastAPI /docs endpoint) — keep updated |
| **Code Architecture Notes** | Folder structure, naming conventions, patterns used |
| **Test Coverage Report** | How much code is covered by tests, critical paths tested |

---

## Phase 6: Frontend Implementation

**Purpose:** Build the UI according to Phase 3 design. Connect with backend APIs.

**Key question:** *"How do I turn the design into a working interface?"*

### Checklist

1. **Project Setup** — Init framework (Vite + React, Next.js, etc.), styling, routing
2. **Build Components** — Follow the component list from Phase 3
3. **State Management** — Server state (React Query/SWR) + client state (Zustand/Redux). Don't overengineer.
4. **API Integration** — Connect to backend endpoints, handle loading/error states
5. **Polish** — Responsive design, loading states, error handling, animations

### Skills Needed

| Skill | Why |
|-------|-----|
| React (or chosen FE framework) | Build interactive UIs |
| Tailwind / CSS | Style components |
| API consumption | Fetch and display data from BE |
| State management | Manage data flow in the UI |

### Tools

- **React + Vite** — Fast FE dev setup
- **TailwindCSS** — Utility-first styling
- **React Query / TanStack Query** — Server state management
- **Recharts / Chart.js** — Data visualization

### Documentation Output (3 docs)

| Document | Description |
|----------|-------------|
| **Component Storybook / Docs** | Document each component: props, usage, variants |
| **State Management Map** | Diagram: what data lives where (server state vs client state) |
| **FE README.md** | Setup guide, folder structure, coding conventions for FE |

---

## Phase 7: Testing & QA

**Purpose:** Test the full flow, edge cases, performance, and security. This phase determines whether the app feels amateur or professional.

**Key question:** *"Does everything work correctly, even in unexpected situations?"*

### Checklist

1. **E2E Testing** — Full user flow from signup to core action
2. **Edge Cases** — What if API is down? Invalid input? Empty data? Expired session?
3. **Performance** — API response time, FE load speed, query optimization, lazy loading
4. **Security** — Input validation, SQL injection, CORS, rate limiting, auth checks

### Skills Needed

| Skill | Why |
|-------|-----|
| Testing mindset | Think about what can go wrong |
| Debugging | Trace and fix issues efficiently |
| Security basics | Protect against common vulnerabilities |

### Tools

- **Playwright / Cypress** — E2E testing
- **Lighthouse** — Performance auditing
- **Postman** — API testing

### Documentation Output (4 docs)

| Document | Description |
|----------|-------------|
| **Test Plan** | All test cases to run, organized by feature |
| **Bug Report Log** | Bug tracking: severity, steps to reproduce, status |
| **Performance Benchmark** | Measurements: API latency, FE load time, Lighthouse scores |
| **Security Checklist** | OWASP top 10 items checked: XSS, CSRF, SQL injection... |

---

## Phase 8: Deploy & Launch

**Purpose:** Put the app on the internet. No deployment = the app doesn't exist. This is the finish line.

**Key question:** *"How do I get this running in production and keep it running?"*

### Checklist

1. **CI/CD Pipeline** — Auto test + deploy on push to main (GitHub Actions)
2. **Deploy Backend** — Cloud platform (Railway, Render, AWS), DB, env vars, domain
3. **Deploy Frontend** — CDN/host (Vercel, Netlify), connect API, custom domain
4. **Monitoring** — Error tracking (Sentry), logging, health check endpoints
5. **Launch!** — Share on LinkedIn, Twitter, Reddit. Collect feedback. Iterate.

### Skills Needed

| Skill | Why |
|-------|-----|
| DevOps basics | Understand servers, environments, deploys |
| CI/CD | Automate the build-test-deploy pipeline |
| Cloud deployment | Get apps running on cloud platforms |

### Tools

- **GitHub Actions** — CI/CD automation
- **Railway / Render** — Backend hosting
- **Vercel / Netlify** — Frontend hosting
- **Sentry** — Error monitoring

### Documentation Output (4 docs)

| Document | Description |
|----------|-------------|
| **Deployment Guide** | Step-by-step: how to deploy BE, FE, DB from scratch |
| **Environment Config** | All env variables needed per environment (dev, staging, prod) |
| **CI/CD Pipeline Doc** | Pipeline description: trigger -> build -> test -> deploy -> notify |
| **Runbook** | Incident handling guide: app down, DB full, API errors... |

---

## Phase 9: Maintenance & Iteration

**Purpose:** The app launching is NOT the end. 80% of a product's lifetime is spent here. Collect feedback, fix bugs, add features, keep the app alive.

**Key question:** *"How do I keep improving and maintaining this?"*

### Checklist

1. **Bug Tracking & Fixing** — Collect bug reports from users + Sentry alerts. Prioritize: Critical > High > Medium > Low
2. **User Feedback Loop** — Collect feedback via surveys, analytics, support. Turn feedback into prioritized feature requests
3. **Performance Monitoring** — Track API response time, error rates, uptime. Set alerts for thresholds
4. **Feature Iteration** — Feedback -> plan new features -> go back to Phase 1 for that feature. This is the "cycle"!
5. **Tech Debt & Refactoring** — V1 code will be ugly — OK. But schedule time to refactor and update dependencies
6. **Documentation Updates** — Update all docs when changes happen. Future you will thank present you

### Skills Needed

| Skill | Why |
|-------|-----|
| Monitoring | Know when things break before users tell you |
| Prioritization | Decide what to fix/build next |
| Refactoring | Improve code quality incrementally |
| User Research | Understand what users actually need |

### Tools

- **Sentry** — Error tracking and alerting
- **Google Analytics** — Usage analytics
- **GitHub Issues** — Bug and feature tracking
- **Notion** — Documentation and planning

### Documentation Output (4 docs)

| Document | Description |
|----------|-------------|
| **Changelog** | Log every change by version: v1.0.1, v1.1.0... (semver) |
| **Feedback & Feature Backlog** | All feedback + feature requests with priority |
| **Post-mortem Reports** | After incidents: what happened, root cause, prevention |
| **Updated Documentation** | All docs from Phase 1-8 updated with latest changes |

---

## Documentation Summary

**Total: 33 documents across 9 phases**

| Phase | Docs | Documents |
|-------|------|-----------|
| 1. Requirements | 3 | PRD, User Stories, MoSCoW |
| 2. System Design | 4 | Architecture, Tech Stack, API Spec, Data Flow |
| 3. UI/UX | 4 | User Flow, Wireframes, Components, Style Guide |
| 4. Database | 3 | ER Diagram, Schema, Migration Plan |
| 5. Backend | 4 | README, API Docs, Architecture Notes, Test Report |
| 6. Frontend | 3 | Component Docs, State Map, FE README |
| 7. Testing | 4 | Test Plan, Bug Log, Performance, Security Checklist |
| 8. Deploy | 4 | Deploy Guide, Env Config, CI/CD Doc, Runbook |
| 9. Maintenance | 4 | Changelog, Backlog, Post-mortems, Updated Docs |

> **Note:** Documentation is not a separate phase — it runs **throughout every phase**. Each phase produces its own output documents.

---

## Related Keywords for Further Research

### Primary
- **SDLC (Software Development Life Cycle)** — The #1 keyword for this entire process

### Per Phase
- **Requirements Engineering** — Phase 1
- **System Design / Software Architecture** — Phase 2
- **UI/UX Design / Wireframing** — Phase 3
- **Database Schema Design / Data Modeling** — Phase 4
- **REST API Design** — Phase 2 + 5
- **CI/CD (Continuous Integration / Deployment)** — Phase 8
- **Software Maintenance** — Phase 9

### Methodology
- **Agile / Scrum** — Iterative sprints, flexible, continuous feedback
- **Waterfall** — Linear, each phase completes before the next starts
- **MVP (Minimum Viable Product)** — Build minimum first, ship fast, get feedback

### Recommended Search
- "SDLC for solo developers"
- "SDLC for indie hackers"

---

## Important Reminders

1. **The roadmap is a spiral, not a straight line.** You will go forward, discover something missing, go back, fix it, and continue. That's normal.
2. **First time through will be messy.** Good developers aren't people who never make mistakes — they're people who know which phase to go back to when problems arise.
3. **Solution Architect courses are NOT needed yet.** SA is for people who've completed many cycles and need to optimize at scale. Complete 2-3 full projects first, then SA becomes extremely valuable.
4. **Don't skip phases.** The whole point is to build the muscle memory of going through every phase. Speed comes with repetition, not shortcuts.
