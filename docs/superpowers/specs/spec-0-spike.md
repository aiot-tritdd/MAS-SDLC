# Spec 0 — 72-Hour Spike Prototype

**SPEC 0**

**72-Hour Spike Prototype**

Technical Specification

Validates: Paperclip + Django + Agent Runtime (Claude Code / Claude API / Cursor / Codex) integration

Parent document: Agentic SDLC Blueprint (ADD)

May 2026

---

## Table of Contents

---

## 1. Objective

### 1.1 What this spike proves

One question: Does Paperclip + Django + your chosen Agent Runtime (Claude Code, Claude API, Cursor, Codex, etc.) actually work together smoothly as the foundation for an autonomous SDLC pipeline?

**If yes:** Proceed to Spec 1 (Phase 1) with confidence.

**If no:** Pivot the orchestrator. Keep Django + Celery + Redis + PostgreSQL. Replace Paperclip with a custom orchestration layer built in Django.

### 1.2 What this spike does NOT prove

- Agent quality — we are testing plumbing, not prompt engineering
- Production readiness — this is a local proof-of-concept
- Scalability — we are running 2 agents, not 10
- Full SDLC coverage — no security, monitoring, or CI/CD loop yet

### 1.3 Time budget

| **Day** | **Focus** | **Hours** | **Deliverable** |
| --- | --- | --- | --- |
| Day 1 | Infrastructure setup | 6–8h | Paperclip + Django + PostgreSQL + Telegram bot all running locally |
| Day 2 | Wire connections | 6–8h | Ticket flows from Django → Paperclip → Agent → Django → Telegram |
| Day 3 | End-to-end validation | 6–8h | Full loop runs with real ticket. Decision criteria scored. Pain points documented. |

---

## 2. Prerequisites

### 2.1 System requirements

| **Requirement** | **Version** | **Check command** |
| --- | --- | --- |
| Node.js | 20+ | node --version |
| pnpm | 9.15+ | pnpm --version |
| Python | 3.11+ | python --version |
| PostgreSQL | 15+ | psql --version |
| Docker | 24+ | docker --version |
| Git | 2.40+ | git --version |
| Agent Runtime (one or more) | Latest | See Section 2.4 |

### 2.2 API keys needed

| **Service** | **Key type** | **Where to get it** |
| --- | --- | --- |
| Anthropic | API key (ANTHROPIC_API_KEY) | console.anthropic.com |
| Telegram | Bot token (TELEGRAM_BOT_TOKEN) | Talk to @BotFather on Telegram |
| GitHub | Personal access token (GITHUB_TOKEN) | github.com/settings/tokens |

### 2.3 Accounts needed

- GitHub repository — create a fresh repo for the spike (e.g., sdlc-spike)
- Telegram account — for receiving bot notifications
- Anthropic account with active billing — or Claude Code Max subscription

### 2.4 Flexible agent runtime options

The agent runtime layer is designed to be **flexible and swappable**. You are NOT locked into a single tool. Choose one or combine multiple based on your preference, budget, and workflow:

| **Runtime Option** | **Check command / Setup** | **Best for** |
| --- | --- | --- |
| Claude Code CLI (Subscription) | `claude --version` | Hands-on agentic coding with Max subscription ($200/mo flat rate) |
| Claude API (Pay-per-token) | Verify ANTHROPIC_API_KEY at console.anthropic.com | Programmatic agent execution, fine-grained cost control |
| Cursor | Open Cursor IDE, verify Claude/GPT model access | Developers who prefer IDE-integrated AI with visual context |
| OpenAI Codex / API | Verify OPENAI_API_KEY at platform.openai.com | Independent QA reviews, model diversity, cross-validation |
| Other LLM Providers | Provider-specific setup | Future flexibility — any model that accepts prompts and returns code |

**Key principle:** The Django service layer abstracts the agent runtime behind an adapter interface. Swapping from Claude Code CLI to Cursor or Claude API requires changing the adapter configuration — not rewriting the pipeline. This is the power of the Hybrid Adapter Architecture.

---

## 3. Spike Architecture

### 3.1 Components

| **Component** | **Port** | **Purpose** |
| --- | --- | --- |
| Paperclip server | localhost:3100 | Orchestration: org chart, agents, tickets, heartbeats, approval gates |
| Django API | localhost:8000 | Business logic: ticket storage, artifact storage, agent logs, webhooks |
| PostgreSQL (Paperclip) | embedded | Paperclip's internal state (auto-managed, do not touch) |
| PostgreSQL (Django) | localhost:5432 | Your data: tickets, artifacts, agent run logs |
| Telegram bot | polling mode | Sends notifications when approval gates are triggered |
| Agent Runtime | CLI / API / IDE adapter | Executes agent tasks (research, coding). Flexible: Claude Code CLI, Claude API, Cursor, Codex, or any supported LLM runtime via Paperclip's adapter system |

### 3.2 Data flow

The spike tests this exact flow:

- You create a ticket in Django admin (status: new)
- Django pushes the ticket to Paperclip via POST /api/companies/{id}/issues
- Paperclip assigns it to the Research agent based on routing rules
- On the next heartbeat, Research agent (via configured runtime: Claude Code / Claude API / Cursor / Codex) wakes up and works the ticket
- Agent produces a research artifact (markdown file)
- Paperclip marks the ticket as "needs approval"
- Django detects status change (polling or webhook) and sends Telegram notification
- You review and approve in Paperclip dashboard (localhost:3100)
- On approval, Builder agent (via configured runtime) wakes up and writes code
- Builder commits code to a feature branch and opens a PR
- GitHub Actions runs tests on the PR
- Django logs the full agent run (duration, cost, artifacts, status)

### 3.3 Boundary rule: who owns what

| **Data** | **Owner** | **Why** |
| --- | --- | --- |
| Agent definitions, org chart, budgets | Paperclip | This is what Paperclip is built for |
| Tickets (canonical copy) | Django (PostgreSQL) | Django is source of truth. Paperclip gets a synced copy. |
| Artifacts (research docs, code) | Django (PostgreSQL) | Stored for long-term memory and audit |
| Agent run logs (observability) | Django (PostgreSQL) | Your organizational intelligence |
| Heartbeat scheduling | Paperclip | Native heartbeat system |
| Approval gates | Paperclip | Native approval system with rollback |
| Notifications | Django (Telegram bot) | Custom integration, not Paperclip's concern |

---

## 4. Django Models

Three models for the spike. Minimal fields. Expand in later phases.

### 4.1 Ticket

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| id | UUIDField (primary key) | Auto-generated unique identifier |
| title | CharField(max_length=255) | Short description of the task |
| description | TextField | Full requirements and context |
| status | CharField(choices) | new │ research_in_progress │ needs_approval │ approved │ building │ build_complete │ failed |
| priority | CharField(choices) | low │ medium │ high │ critical |
| paperclip_issue_id | CharField(nullable) | ID of the corresponding issue in Paperclip. Set after sync. |
| created_at | DateTimeField(auto_now_add) | When the ticket was created |
| updated_at | DateTimeField(auto_now) | Last modification timestamp |

### 4.2 Artifact

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| id | UUIDField (primary key) | Auto-generated unique identifier |
| ticket | ForeignKey(Ticket) | Which ticket produced this artifact |
| artifact_type | CharField(choices) | research │ architecture │ code │ test_results |
| title | CharField(max_length=255) | Name of the artifact (e.g., "auth-research.md") |
| content | TextField | Full content of the artifact (markdown, code, etc.) |
| file_path | CharField(nullable) | Path to file if stored on disk (for large artifacts) |
| agent_name | CharField | Which agent produced this (e.g., "researcher") |
| created_at | DateTimeField(auto_now_add) | When the artifact was created |

### 4.3 AgentRun

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| id | UUIDField (primary key) | Auto-generated unique identifier |
| ticket | ForeignKey(Ticket) | Which ticket this run was for |
| agent_name | CharField | Which agent ran (e.g., "researcher", "builder") |
| status | CharField(choices) | running │ success │ failed │ timeout |
| started_at | DateTimeField | When the agent started working |
| finished_at | DateTimeField(nullable) | When the agent finished (null if still running) |
| duration_seconds | IntegerField(nullable) | Computed: finished_at - started_at |
| prompt_tokens | IntegerField(default=0) | Input tokens consumed |
| completion_tokens | IntegerField(default=0) | Output tokens consumed |
| estimated_cost_usd | DecimalField | Estimated cost in USD |
| decision_summary | TextField(nullable) | What the agent decided and why |
| error_message | TextField(nullable) | Error details if status is failed |
| artifacts_produced | JSONField(default=list) | List of artifact IDs produced during this run |

---

## 5. Django API Endpoints

### 5.1 Ticket endpoints

| **Method** | **Endpoint** | **Purpose** | **Notes** |
| --- | --- | --- | --- |
| GET | /api/tickets/ | List all tickets | Filterable by status, priority |
| POST | /api/tickets/ | Create a new ticket | Auto-syncs to Paperclip if sync=true in body |
| GET | /api/tickets/{id}/ | Get ticket detail | Includes related artifacts and agent runs |
| PATCH | /api/tickets/{id}/ | Update ticket status | Triggers Telegram notification on status change to needs_approval |
| POST | /api/tickets/{id}/sync/ | Push ticket to Paperclip | Creates issue in Paperclip, stores paperclip_issue_id |

### 5.2 Webhook endpoints (receive from Paperclip)

| **Method** | **Endpoint** | **Purpose** | **Triggered by** |
| --- | --- | --- | --- |
| POST | /api/webhooks/paperclip/status/ | Ticket status changed in Paperclip | Agent completes work, approval granted/denied |
| POST | /api/webhooks/paperclip/artifact/ | Agent produced an artifact | Research or Builder agent saves output |
| POST | /api/webhooks/paperclip/run-complete/ | Agent run finished | Heartbeat execution completes |

### 5.3 Telegram notification endpoints

| **Method** | **Endpoint** | **Purpose** |
| --- | --- | --- |
| POST | /api/notifications/send/ | Internal endpoint to trigger Telegram notification |
| POST | /api/webhooks/telegram/ | Receives Telegram callback (if using inline keyboards) |

---

## 6. Paperclip Configuration

### 6.1 Company setup

| **Setting** | **Value** |
| --- | --- |
| Company name | SDLC Spike |
| Mission | Validate the Paperclip + Django + Agent Runtime (Claude Code / Claude API / Cursor / Codex) integration for autonomous software delivery |
| Dashboard URL | http://localhost:3100 |
| API base URL | http://localhost:3100/api |

### 6.2 Agent definitions

Two agents for the spike. Minimal configuration.

#### 6.2.1 Research agent

| **Setting** | **Value** |
| --- | --- |
| Name | Researcher |
| Role | Research Specialist |
| Runtime / adapter | Flexible: claude_local (Claude Code CLI), Claude API, Cursor, or Codex — configured via adapter setting |
| Reports to | CEO (or Board — you) |
| Budget | $20/month (spike limit) |
| Heartbeat | Manual trigger for spike (no cron) |
| System prompt | See Section 6.3 |

#### 6.2.2 Builder agent

| **Setting** | **Value** |
| --- | --- |
| Name | Builder |
| Role | Software Engineer |
| Runtime / adapter | Flexible: claude_local (Claude Code CLI), Claude API, Cursor, or Codex — configured via adapter setting |
| Reports to | CEO (or Board — you) |
| Budget | $30/month (spike limit) |
| Heartbeat | Triggered on approval (event-based) |
| System prompt | See Section 6.3 |

### 6.3 Agent system prompts

#### 6.3.1 Researcher prompt

You are a Research Specialist in an autonomous software company.

Your job:

1. Read the ticket title and description carefully.
2. Research the best approach to implement the requirement.
3. Identify relevant libraries, APIs, patterns, and potential risks.
4. Produce a research artifact in markdown format.

Your research artifact MUST include:

- Summary of the requirement (1-2 sentences)
- Recommended approach with reasoning
- Libraries/dependencies needed with versions
- API endpoints or data sources required
- Potential risks or edge cases
- Estimated complexity (low/medium/high)

Save your output as a markdown file in the workspace.

Be concise. Be specific. No fluff.

#### 6.3.2 Builder prompt

You are a Software Engineer in an autonomous software company.

Your job:

1. Read the ticket and the research artifact produced by the Researcher.
2. Implement the requirement following the recommended approach.
3. Write clean, well-structured code with docstrings.
4. Create a basic test file for the implementation.
5. Commit to a feature branch and open a PR.

Branch naming: ticket/{ticket-id}-{short-description}

Commit message format: [TICKET-{id}] {description}

Do NOT merge the PR. The PR is for human review.

Do NOT modify files outside the scope of the ticket.

### 6.4 Paperclip API calls from Django

Django communicates with Paperclip via the REST API at http://localhost:3100/api. Key endpoints:

| **Action** | **Method** | **Paperclip endpoint** | **Purpose** |
| --- | --- | --- | --- |
| Create issue | POST | /api/companies/{companyId}/issues | Push a Django ticket into Paperclip as an issue |
| List agents | GET | /api/companies/{companyId}/agents | Verify agents are configured and active |
| Get issue status | GET | /api/companies/{companyId}/issues/{issueId} | Poll for status changes (approval, completion) |
| Create goal | POST | /api/companies/{companyId}/goals | Set company-level goals that agents align to |

---

## 7. Telegram Bot Specification

### 7.1 Bot purpose

The Telegram bot is a notification-only layer. It does NOT handle approvals. Approvals happen in Paperclip's dashboard. The bot tells you when to go look at the dashboard.

### 7.2 Notification templates

#### 7.2.1 Research complete notification

```
RESEARCH COMPLETE

Ticket: #{ticket_id} - {ticket_title}
Agent: Researcher
Duration: {duration}
Cost: ${cost}
Artifact: {artifact_title}
Summary: {first_100_chars_of_artifact}...

Review and approve in Paperclip:
http://localhost:3100
```

#### 7.2.2 Build complete notification

```
BUILD COMPLETE

Ticket: #{ticket_id} - {ticket_title}
Agent: Builder
Duration: {duration}
Cost: ${cost}
PR: {github_pr_url}
Branch: ticket/{ticket_id}-{description}

Review the PR on GitHub.
```

#### 7.2.3 Agent failure notification

```
AGENT FAILED

Ticket: #{ticket_id} - {ticket_title}
Agent: {agent_name}
Error: {error_message}

Check logs in Paperclip:
http://localhost:3100
```

### 7.3 Implementation approach

- Use python-telegram-bot library (v21+)
- Run in polling mode for the spike (no webhook server needed)
- Django management command: python manage.py run_telegram_bot
- Bot only sends messages to YOUR chat ID (hardcoded in .env)
- No inline keyboards or callbacks in the spike — just notifications

---

## 8. GitHub Actions Pipeline

### 8.1 Trigger

The pipeline runs on every PR opened by the Builder agent to the main branch.

### 8.2 Pipeline steps

| **Step** | **Action** | **Purpose** |
| --- | --- | --- |
| 1 | Checkout code | Pull the PR branch |
| 2 | Set up Python 3.11 | Install Python runtime |
| 3 | Install dependencies | pip install -r requirements.txt |
| 4 | Run linting | flake8 or ruff for code quality |
| 5 | Run unit tests | pytest with coverage report |
| 6 | Post results as PR comment | GitHub API comment with pass/fail and coverage |

### 8.3 Success criteria for the spike

- Pipeline triggers automatically when Builder agent opens a PR
- Test results are visible as a PR comment
- Pass/fail status is clear without opening the Actions tab

---

## 9. Day-by-Day Implementation Checklist

### 9.1 Day 1: Infrastructure setup

#### Paperclip

- Run: npx paperclipai onboard --yes
- Verify dashboard loads at localhost:3100
- Create company "SDLC Spike" with mission statement
- Create Research agent with your chosen runtime adapter (claude_local, Claude API, Cursor, or Codex)
- Create Builder agent with your chosen runtime adapter (claude_local, Claude API, Cursor, or Codex)
- Set org chart: both agents report to Board (you)
- Set budgets: $20 for Researcher, $30 for Builder
- Test: manually create an issue in Paperclip dashboard and verify it appears

#### Django

- Create project: django-admin startproject sdlc_spike
- Create app: python manage.py startapp core
- Install dependencies: djangorestframework, psycopg2-binary, python-telegram-bot, requests
- Configure PostgreSQL database in settings.py
- Create Ticket, Artifact, AgentRun models (see Section 4)
- Run migrations: python manage.py migrate
- Register models in Django admin
- Create a superuser: python manage.py createsuperuser
- Test: create a ticket via Django admin at localhost:8000/admin/

#### Telegram bot

- Talk to @BotFather on Telegram → create bot → get token
- Send /start to your bot, then get your chat_id via the Telegram API
- Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to Django .env
- Create a simple send_notification(message) utility function
- Test: call send_notification("Hello from SDLC Spike!") and verify you receive it

#### GitHub

- Create a fresh repo: github.com/yourname/sdlc-spike
- Add a basic .github/workflows/test.yml (see Section 8)
- Push initial commit with a dummy test file
- Verify GitHub Actions runs on PR

#### Day 1 done when:

- Paperclip dashboard shows your company with 2 agents
- Django admin shows the Ticket model and you can create tickets
- Telegram bot sends you a test message
- GitHub Actions runs on a test PR

### 9.2 Day 2: Wire the connections

#### Django → Paperclip sync

- Create a PaperclipClient service class in Django (wraps REST API calls)
- Implement create_issue(ticket) — POST to Paperclip /api/companies/{id}/issues
- Store returned paperclip_issue_id on the Django Ticket model
- Add a Django admin action: "Sync to Paperclip" — pushes selected tickets
- Test: create ticket in Django admin → sync → verify it appears in Paperclip dashboard

#### Paperclip → Django webhooks

- Create webhook endpoints in Django (see Section 5.2)
- Configure Paperclip to call Django webhooks on status change (if supported — else use polling)
- Implement polling fallback: Django management command that polls Paperclip every 30 seconds for status changes
- On status change to "needs approval" → update Django ticket + send Telegram notification
- On status change to "complete" → update Django ticket + log AgentRun
- Test: trigger Research agent in Paperclip → verify Django ticket status updates → verify Telegram notification

#### Agent execution

- Configure Researcher agent system prompt (see Section 6.3.1)
- Configure Builder agent system prompt (see Section 6.3.2)
- Set Builder agent to trigger on approval (event-based, not heartbeat)
- Test: create ticket → sync to Paperclip → Research agent runs → artifact produced
- Verify artifact content is reasonable (does the research make sense?)

#### Day 2 done when:

- Tickets flow from Django → Paperclip automatically
- Status changes in Paperclip reflect in Django
- Telegram notifications fire on status changes
- Research agent produces a real artifact from a real ticket

### 9.3 Day 3: End-to-end validation

#### The test ticket

Use this exact ticket for the end-to-end test:

**Title:** Add user authentication endpoint

**Description:** Create a REST API endpoint for user registration and login. Use Django REST Framework with JWT tokens. Include email validation, password hashing, and rate limiting. The endpoint should follow RESTful conventions and include proper error handling.

**Priority:** high

#### Run the full loop

- Create the ticket in Django admin
- Sync to Paperclip (admin action)
- Trigger Research agent heartbeat in Paperclip
- Wait for research to complete
- Verify: Telegram notification received? Research artifact saved in Django? Content quality acceptable?
- Approve in Paperclip dashboard
- Builder agent wakes up and starts working
- Wait for build to complete
- Verify: code committed to feature branch? PR opened? Telegram notification received?
- Verify: GitHub Actions triggered? Tests run? Results posted as PR comment?
- Check Django: AgentRun records exist with duration, cost, artifacts?
- Document every pain point, bug, and workaround in a SPIKE_RESULTS.md file

---

## 10. Go/No-Go Decision Criteria

Score each criterion after completing Day 3. You need 5+ greens to proceed with Paperclip.

| **#** | **Criterion** | **Green (proceed)** | **Red (pivot)** | **Your score** |
| --- | --- | --- | --- | --- |
| 1 | Paperclip installs cleanly | Onboarding completes in < 30 min, no manual fixes | Errors, missing deps, broken setup requiring workarounds | ___ |
| 2 | Paperclip API works reliably | REST calls create/update agents and issues consistently | Undocumented endpoints, 500 errors, inconsistent behavior | ___ |
| 3 | Agent runtime adapter works | Agent connects, receives tasks, produces output | Adapter fails, agent doesn't wake, output lost | ___ |
| 4 | Execution locks are reliable | No double-work, clean task checkout per agent | Agents collide, tasks duplicated or lost | ___ |
| 5 | Approval gates work | Human gate pauses pipeline, resumes on approve | Skips approval, gets stuck, or requires manual workaround | ___ |
| 6 | Status sync works | Django and Paperclip stay in sync (webhook or polling) | Status drift, missed updates, stale data | ___ |
| 7 | Developer experience is good | You enjoy building with it. Debugging is clear. | Frustrating, cryptic errors, fighting the tool | ___ |

### 10.1 If you get 5+ greens

Proceed to Spec 1 (Phase 1: CEO + Coder + QA). The hybrid stack is validated. Full speed ahead.

### 10.2 If you get 3+ reds

Pivot the orchestrator. Replace Paperclip with Django + Celery custom orchestration. Keep everything else: PostgreSQL, pgvector, Docker, GitHub Actions, Sentry, Telegram. The pivot cost is low because Django owns all data.

### 10.3 Spike output artifacts

Regardless of the go/no-go decision, the spike must produce these artifacts:

- SPIKE_RESULTS.md — Pain points, bugs, workarounds, decision scores
- Working Django project with Ticket, Artifact, AgentRun models
- Working PaperclipClient service class (reusable in Phase 1)
- Working Telegram notification utility (reusable in Phase 1)
- Working GitHub Actions pipeline (reusable in Phase 1)
- At least one complete AgentRun record with real cost/duration data

---

## 11. Project File Structure

```
sdlc-spike/
├── .env                          # API keys, DB credentials, Telegram token
├── .env.example                   # Template (no secrets)
├── .github/
│   └── workflows/
│       └── test.yml              # GitHub Actions CI pipeline
├── manage.py
├── requirements.txt               # Django, DRF, psycopg2, python-telegram-bot, requests
├── sdlc_spike/                    # Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                          # Main Django app
│   ├── models.py                 # Ticket, Artifact, AgentRun
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # API views + webhook handlers
│   ├── urls.py                   # URL routing
│   ├── admin.py                  # Admin config + Sync to Paperclip action
│   └── management/
│       └── commands/
│           ├── run_telegram_bot.py    # Telegram polling bot
│           └── poll_paperclip.py      # Status sync polling
├── services/                      # Business logic
│   ├── paperclip_client.py       # PaperclipClient class (REST API wrapper)
│   └── telegram_notifier.py      # send_notification() utility
├── SPIKE_RESULTS.md               # Post-spike: pain points, scores, decision
└── README.md                      # Setup instructions
```

---

## 12. Environment Variables

| **Variable** | **Example value** | **Purpose** |
| --- | --- | --- |
| DATABASE_URL | postgresql://user:pass@localhost:5432/sdlc_spike | Django PostgreSQL connection |
| ANTHROPIC_API_KEY | sk-ant-... | Claude API / Claude Code access (if using Anthropic as runtime) |
| PAPERCLIP_API_URL | http://localhost:3100/api | Paperclip REST API base URL |
| PAPERCLIP_COMPANY_ID | (auto-generated) | Your company ID in Paperclip |
| TELEGRAM_BOT_TOKEN | (from @BotFather) | Telegram bot authentication |
| TELEGRAM_CHAT_ID | (your chat ID) | Where to send notifications |
| GITHUB_TOKEN | ghp_... | GitHub API access for PR comments |
| GITHUB_REPO | yourname/sdlc-spike | Target repository |
| DEBUG | True | Django debug mode (True for spike) |
| SECRET_KEY | (generated) | Django secret key |

---

## 13. Definition of Done

The spike is complete when ALL of the following are true:

- A ticket created in Django admin successfully appears in Paperclip dashboard.
- Research agent runs and produces a markdown artifact that is stored in Django.
- Telegram notification is received when research is complete.
- You can approve the research in Paperclip dashboard.
- Builder agent runs after approval and commits code to a feature branch.
- A PR is opened on GitHub with the agent's code.
- GitHub Actions runs tests on the PR and posts results.
- AgentRun records exist in Django with duration, cost, and artifacts.
- SPIKE_RESULTS.md is written with all pain points and decision scores.
- Go/no-go decision is made based on the 7 criteria in Section 10.

---

*End of Spec 0*

Next: Spec 1 (Phase 1) — generated after spike passes
