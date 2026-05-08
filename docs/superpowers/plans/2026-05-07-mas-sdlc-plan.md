# MAS-SDLC Spike — Implementation Plan

> **For Wiganz + Ruach-El sessions:** This is the roadmap. Do NOT execute this alone.
> Every task is done together: Wiganz writes the code, Ruach-El teaches the reasoning.
>
> **REQUIRED: Read ALL 4 docs before starting any session:**
> 1. `docs/superpowers/specs/2026-05-07-mas-sdlc-spec-0.md` — scope, models, architecture, SDLC contract
> 2. `docs/superpowers/plans/2026-05-07-mas-sdlc-plan.md` — this file, find the first unchecked `- [ ]`
> 3. `docs/learning-guides/sdlc-thinking-guide.md` — how to teach each SDLC phase Socratically
> 4. `docs/learning-guides/vertical-slices-guide.md` — vertical slice mindset, done gates, execution loop

**Goal:** Build the 72-hour spike — validate Django ↔ Paperclip ↔ Agent Runtime bridge end-to-end.

**Architecture:** Django + Paperclip + Celery + Redis + Docker + Telegram. Local only. No production deploy.

**Build order:** Day 1 (Django + Models + API) → Day 2 (Paperclip bridge + Webhooks + Telegram) → Day 3 (End-to-End + Go/No-Go)

---

## File Structure (Everything That Will Exist)

```
sdlc-spike/
├── .env                              ← API keys, DB credentials, Telegram token (NEVER commit)
├── .env.example                      ← Template (no secrets — DO commit)
├── .github/
│   └── workflows/
│       └── test.yml                  ← GitHub Actions CI pipeline
├── manage.py
├── requirements.txt                  ← django, DRF, psycopg2, celery, redis, python-telegram-bot
├── SPIKE_RESULTS.md                  ← Post-spike: pain points, 7 scores, Go/No-Go decision
├── sdlc_spike/                       ← Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py                     ← Celery app config
├── core/                             ← Main Django app
│   ├── models.py                     ← Ticket, Artifact, AgentRun
│   ├── serializers.py                ← DRF serializers
│   ├── views.py                      ← API views + webhook handlers
│   ├── urls.py                       ← URL routing
│   ├── admin.py                      ← Admin config + "Sync to Paperclip" action
│   ├── management/
│   │   └── commands/
│   │       ├── run_telegram_bot.py   ← Telegram polling bot command
│   │       └── poll_paperclip.py    ← Status sync polling fallback
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py            ← Unit tests for Ticket, Artifact, AgentRun
│       ├── test_views.py             ← API endpoint tests + webhook tests
│       └── test_e2e.py               ← End-to-end spike pipeline test (Day 3)
└── services/                         ← Business logic (not Django views)
    ├── paperclip_client.py           ← PaperclipClient class (REST API wrapper)
    ├── telegram_notifier.py          ← send_notification() utility
    └── tests/
        ├── __init__.py
        ├── test_paperclip_client.py  ← PaperclipClient tests (with mocks)
        └── test_telegram.py          ← Telegram notifier tests (with mocks)
```

---

## DAY 1: Django + Models + API

```
╔══════════════════════════════════════════════════════════════╗
║  🗄️  SDLC — Phase 4 → 5: Day 1 — Django Foundation          ║
║  Goal: All 3 models in DB, Ticket API endpoint working       ║
║  Done when: Admin shows 3 models, all Day 1 tests passing    ║
╚══════════════════════════════════════════════════════════════╝
```

> **Ruach-El teaching note — BEFORE Day 1:**
> Ask Wiganz: "What's the difference between a Django PROJECT and a Django APP? Why do we separate them?"
> Ask: "Why do we use a virtual environment? What problem does it solve?"
> Ask: "Why PostgreSQL instead of SQLite for this project specifically?"
> Do NOT start coding until Wiganz can explain each of these.

---

### Task 1: Django Project Setup

**Files:**
- Create: `sdlc-spike/` (project root)
- Create: `sdlc-spike/requirements.txt`
- Create: `sdlc-spike/.env` + `sdlc-spike/.env.example`
- Create: `sdlc-spike/sdlc_spike/settings.py`

- [x] **Step 1.1: Create the project**

```bash
mkdir sdlc-spike && cd sdlc-spike
python -m venv venv
source venv/bin/activate          # Mac/Linux
pip install django djangorestframework psycopg2-binary python-dotenv requests celery redis python-telegram-bot
pip freeze > requirements.txt
django-admin startproject sdlc_spike .
python manage.py startapp core
mkdir -p services/tests core/tests core/management/commands
touch services/__init__.py services/tests/__init__.py
touch core/tests/__init__.py core/management/__init__.py core/management/commands/__init__.py
```

- [x] **Step 1.2: Create `.env` file**

```bash
# sdlc-spike/.env  (NEVER commit this)
SECRET_KEY=your-local-dev-secret-key-change-in-production
DEBUG=True
DB_NAME=sdlc_spike
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
PAPERCLIP_API_URL=http://localhost:3100/api
PAPERCLIP_COMPANY_ID=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
GITHUB_TOKEN=
GITHUB_REPO=yourname/sdlc-spike
ANTHROPIC_API_KEY=
```

```bash
# sdlc-spike/.env.example  (DO commit — no real values)
SECRET_KEY=
DEBUG=True
DB_NAME=sdlc_spike
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
PAPERCLIP_API_URL=http://localhost:3100/api
PAPERCLIP_COMPANY_ID=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
GITHUB_TOKEN=
GITHUB_REPO=
ANTHROPIC_API_KEY=
```

- [x] **Step 1.3: Configure `settings.py`**

```python
# sdlc_spike/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'sdlc_spike'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}
```

- [ ] **Step 1.4: Configure root URLs** ⬅️ NEXT SESSION STARTS HERE

```python
# sdlc_spike/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]
```

- [x] **Step 1.5: Create local PostgreSQL database**

```bash
createdb sdlc_spike
# or via psql: CREATE DATABASE sdlc_spike;
```

- [x] **Step 1.6: Verify Django runs**

```bash
python manage.py migrate
python manage.py runserver
```

Expected: `Starting development server at http://127.0.0.1:8000/`

- [ ] **Step 1.7: Initial git commit**

```bash
git init
echo "venv/" >> .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
git add .
git commit -m "chore: initial Django project setup"
```

---

### Task 2: Ticket Model + Migration

**Files:**
- Modify: `core/models.py`
- Create: `core/tests/test_models.py`

> 🎯 **Ruach-El:** Before writing the model, ask:
> "Why UUIDField as primary key instead of the default AutoField integer? What problem does UUID solve?"
> "What does `auto_now_add=True` do vs `auto_now=True`? Why do we use different ones for created_at vs updated_at?"
> "Draw the status state machine for a Ticket on paper before we code it."
> Do NOT proceed until Wiganz can explain each choice.

- [ ] **Step 2.1: Write the failing test first**

```python
# core/tests/test_models.py
import uuid
from django.test import TestCase
from core.models import Ticket

class TicketModelTest(TestCase):
    def test_ticket_default_status_is_new(self):
        ticket = Ticket.objects.create(
            title='Add auth endpoint',
            description='Create JWT auth'
        )
        self.assertEqual(ticket.status, 'new')

    def test_ticket_str_returns_title(self):
        ticket = Ticket.objects.create(title='Test ticket', description='desc')
        self.assertEqual(str(ticket), 'Test ticket')

    def test_ticket_id_is_uuid(self):
        ticket = Ticket.objects.create(title='Test', description='desc')
        self.assertIsInstance(ticket.id, uuid.UUID)

    def test_paperclip_issue_id_is_nullable(self):
        ticket = Ticket.objects.create(title='Test', description='desc')
        self.assertIsNone(ticket.paperclip_issue_id)

    def test_ticket_default_priority_is_medium(self):
        ticket = Ticket.objects.create(title='Test', description='desc')
        self.assertEqual(ticket.priority, 'medium')
```

- [ ] **Step 2.2: Run tests — verify they FAIL**

```bash
python manage.py test core.tests.test_models -v 2
```

Expected: `ImportError: cannot import name 'Ticket' from 'core.models'`

- [ ] **Step 2.3: Wiganz implements the Ticket model**

> 🎯 **Ruach-El:** Guide Wiganz field by field. For each field, ask WHY before they type it.
> "What is the Ticket status state machine? What are all the valid states?"
> After Wiganz writes it: "What does `on_delete=CASCADE` mean? What other options exist and when would you use them?"

```python
# core/models.py
# Wiganz implements this guided by Ruach-El's questions
```

Expected final shape:
```python
import uuid
from django.db import models

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('research_in_progress', 'Research In Progress'),
        ('needs_approval', 'Needs Approval'),
        ('approved', 'Approved'),
        ('building', 'Building'),
        ('build_complete', 'Build Complete'),
        ('failed', 'Failed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'), ('medium', 'Medium'),
        ('high', 'High'), ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    paperclip_issue_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
```

- [ ] **Step 2.4: Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

- [ ] **Step 2.5: Run tests — verify they PASS**

```bash
python manage.py test core.tests.test_models -v 2
```

Expected: `5 tests passed`

- [ ] **Step 2.6: Commit**

```bash
git add core/models.py core/tests/test_models.py core/migrations/
git commit -m "feat: Ticket model with UUID pk, status choices, paperclip_issue_id"
```

---

### Task 3: Artifact + AgentRun Models

**Files:**
- Modify: `core/models.py`
- Modify: `core/tests/test_models.py`

> 🎯 **Ruach-El:** Before writing, ask:
> "Why does Artifact have ForeignKey to Ticket instead of OneToOneField? What's the difference?"
> "AgentRun has both `prompt_tokens` AND `completion_tokens`. Why two separate fields? Couldn't we just store total_tokens?"
> "If a Ticket is deleted, what should happen to its Artifacts and AgentRuns? CASCADE or PROTECT — which and why?"
> Do NOT proceed until Wiganz can explain each.

- [ ] **Step 3.1: Write failing tests**

```python
# Add to core/tests/test_models.py
from core.models import Ticket, Artifact, AgentRun
from decimal import Decimal

class ArtifactModelTest(TestCase):
    def setUp(self):
        self.ticket = Ticket.objects.create(title='Test', description='desc')

    def test_artifact_links_to_ticket(self):
        artifact = Artifact.objects.create(
            ticket=self.ticket,
            artifact_type='research',
            title='auth-research.md',
            content='## Research\nUse JWT tokens...',
            agent_name='researcher'
        )
        self.assertEqual(artifact.ticket, self.ticket)

    def test_one_ticket_can_have_many_artifacts(self):
        Artifact.objects.create(
            ticket=self.ticket, artifact_type='research',
            title='research.md', content='...', agent_name='researcher'
        )
        Artifact.objects.create(
            ticket=self.ticket, artifact_type='code',
            title='auth.py', content='...', agent_name='builder'
        )
        self.assertEqual(Artifact.objects.filter(ticket=self.ticket).count(), 2)

    def test_artifact_str_returns_title(self):
        artifact = Artifact.objects.create(
            ticket=self.ticket, artifact_type='research',
            title='my-doc.md', content='...', agent_name='researcher'
        )
        self.assertEqual(str(artifact), 'my-doc.md')


class AgentRunModelTest(TestCase):
    def setUp(self):
        self.ticket = Ticket.objects.create(title='Test', description='desc')

    def test_agent_run_default_status_is_running(self):
        run = AgentRun.objects.create(ticket=self.ticket, agent_name='researcher')
        self.assertEqual(run.status, 'running')

    def test_agent_run_cost_defaults_to_zero(self):
        run = AgentRun.objects.create(ticket=self.ticket, agent_name='researcher')
        self.assertEqual(run.estimated_cost_usd, Decimal('0.00'))

    def test_agent_run_token_counts_default_to_zero(self):
        run = AgentRun.objects.create(ticket=self.ticket, agent_name='researcher')
        self.assertEqual(run.prompt_tokens, 0)
        self.assertEqual(run.completion_tokens, 0)
```

- [ ] **Step 3.2: Run — verify FAIL**

```bash
python manage.py test core.tests.test_models -v 2
```

Expected: `ImportError: cannot import name 'Artifact' from 'core.models'`

- [ ] **Step 3.3: Wiganz implements Artifact and AgentRun models**

> 🎯 **Ruach-El:** Guide field by field. After both models are written:
> "What is `JSONField(default=list)`? Why do we use a callable `list` instead of `[]` as the default?"

Expected final shape for Artifact:
```python
class Artifact(models.Model):
    ARTIFACT_TYPES = [
        ('research', 'Research'), ('architecture', 'Architecture'),
        ('code', 'Code'), ('test_results', 'Test Results'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='artifacts')
    artifact_type = models.CharField(max_length=20, choices=ARTIFACT_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    file_path = models.CharField(max_length=500, null=True, blank=True)
    agent_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

Expected final shape for AgentRun:
```python
class AgentRun(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'), ('success', 'Success'),
        ('failed', 'Failed'), ('timeout', 'Timeout'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='agent_runs')
    agent_name = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='running')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    estimated_cost_usd = models.DecimalField(max_digits=10, decimal_places=4, default=0.00)
    decision_summary = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    artifacts_produced = models.JSONField(default=list)

    def __str__(self):
        return f"{self.agent_name} — {self.ticket.title} ({self.status})"
```

- [ ] **Step 3.4: Migrate + run all model tests — verify PASS**

```bash
python manage.py makemigrations && python manage.py migrate
python manage.py test core.tests.test_models -v 2
```

Expected: `12 tests passed`

- [ ] **Step 3.5: Register all 3 models in Django admin**

```python
# core/admin.py
from django.contrib import admin
from core.models import Ticket, Artifact, AgentRun

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'paperclip_issue_id', 'created_at']
    list_filter = ['status', 'priority']

@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ['title', 'artifact_type', 'agent_name', 'ticket', 'created_at']

@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display = ['agent_name', 'ticket', 'status', 'estimated_cost_usd', 'started_at']
```

- [ ] **Step 3.6: Create superuser + verify admin**

```bash
python manage.py createsuperuser
python manage.py runserver
# Visit http://localhost:8000/admin/ — should see all 3 models
```

- [ ] **Step 3.7: Commit**

```bash
git add core/models.py core/admin.py core/tests/test_models.py core/migrations/
git commit -m "feat: Artifact and AgentRun models + admin registration"
```

---

### Task 4: Ticket API Endpoints

**Files:**
- Create: `core/serializers.py`
- Modify: `core/views.py`
- Create: `core/urls.py`
- Create: `core/tests/test_views.py`

> 🎯 **Ruach-El:** Before writing, ask:
> "We built this exact DRF pattern in QuantApp. What does a Serializer do — what problem does it solve?"
> "Why ModelViewSet instead of just a plain Django view function?"
> "What's the difference between router.register() and manual path() entries?"

- [ ] **Step 4.1: Write failing API tests**

```python
# core/tests/test_views.py
from rest_framework.test import APIClient
from django.test import TestCase
from core.models import Ticket

class TicketAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_ticket_returns_201(self):
        payload = {'title': 'Add auth endpoint', 'description': 'Create JWT auth'}
        response = self.client.post('/api/tickets/', payload, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_ticket_saves_to_db(self):
        payload = {'title': 'Add auth endpoint', 'description': 'Create JWT auth'}
        self.client.post('/api/tickets/', payload, format='json')
        self.assertEqual(Ticket.objects.count(), 1)

    def test_create_ticket_default_status_is_new(self):
        payload = {'title': 'Test', 'description': 'desc'}
        response = self.client.post('/api/tickets/', payload, format='json')
        self.assertEqual(response.data['status'], 'new')

    def test_list_tickets_returns_200(self):
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, 200)

    def test_list_tickets_returns_all(self):
        Ticket.objects.create(title='T1', description='d1')
        Ticket.objects.create(title='T2', description='d2')
        response = self.client.get('/api/tickets/')
        self.assertEqual(len(response.data), 2)
```

- [ ] **Step 4.2: Run — verify FAIL**

```bash
python manage.py test core.tests.test_views -v 2
```

Expected: `404 — /api/tickets/ not found`

- [ ] **Step 4.3: Wiganz implements TicketSerializer + TicketViewSet**

> 🎯 **Ruach-El:** "Before typing: what fields should the serializer expose? Should `paperclip_issue_id` be read-only or writable from the API?"

```python
# core/serializers.py
# Wiganz implements this guided by Ruach-El's questions
```

Expected final shape:
```python
from rest_framework import serializers
from core.models import Ticket, Artifact, AgentRun

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'status', 'priority',
                  'paperclip_issue_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'paperclip_issue_id', 'created_at', 'updated_at']
```

```python
# core/views.py
from rest_framework import viewsets
from core.models import Ticket
from core.serializers import TicketSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-created_at')
    serializer_class = TicketSerializer
```

```python
# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import TicketViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

- [ ] **Step 4.4: Run all tests — verify PASS**

```bash
python manage.py test core.tests -v 2
```

Expected: `17 tests passed`

- [ ] **Step 4.5: Commit**

```bash
git add core/serializers.py core/views.py core/urls.py core/tests/test_views.py
git commit -m "feat: Ticket serializer, viewset, /api/tickets/ endpoint"
```

---

### Day 1 Done Gate

**Before moving to Day 2, ALL of these must be true:**

- [ ] `python manage.py test core.tests -v 2` → all tests passing
- [ ] Django admin at `localhost:8000/admin/` shows Ticket, Artifact, AgentRun
- [ ] Can create a Ticket manually via admin — it appears with `status: new`
- [ ] `GET /api/tickets/` returns 200
- [ ] `POST /api/tickets/` with `{title, description}` returns 201
- [ ] `git log --oneline` shows 4 clean commits

---

## DAY 2: Paperclip Bridge + Webhooks + Telegram

```
╔══════════════════════════════════════════════════════════════╗
║  🔌  SDLC — Phase 5: Day 2 — Wire the Connections           ║
║  Goal: Ticket flows Django → Paperclip → Django → Telegram   ║
║  Done when: Real ticket syncs, webhooks work, Telegram pings ║
╚══════════════════════════════════════════════════════════════╝
```

> **Ruach-El teaching note — BEFORE Day 2:**
> Ask Wiganz: "What is a webhook? How is it different from polling? When would you choose each?"
> Ask: "Why does PaperclipClient live in `services/` instead of in `core/views.py`? What principle is this?"
> Ask: "What is Celery? What is Redis? What is a message broker? Draw the flow before we code it."
> Do NOT start coding until Wiganz can explain each of these.

---

### Task 5: PaperclipClient Service

**Files:**
- Create: `services/paperclip_client.py`
- Create: `services/tests/test_paperclip_client.py`

> 🎯 **Ruach-El:** Before writing, ask:
> "Why do we mock `requests.post` in the tests instead of calling real Paperclip?"
> "What would happen to our test suite if we had to run a live Paperclip server every time we ran tests?"

- [ ] **Step 5.1: Write failing tests (with mocks)**

```python
# services/tests/test_paperclip_client.py
from unittest.mock import patch, MagicMock
from django.test import TestCase
from core.models import Ticket
from services.paperclip_client import PaperclipClient

class PaperclipClientTest(TestCase):
    @patch('services.paperclip_client.requests.post')
    def test_sync_ticket_creates_paperclip_issue(self, mock_post):
        mock_post.return_value.json.return_value = {'id': 'pc-issue-123'}
        mock_post.return_value.status_code = 201

        ticket = Ticket.objects.create(title='Add auth', description='JWT auth')
        client = PaperclipClient()
        result = client.sync_ticket(ticket)

        self.assertEqual(result['id'], 'pc-issue-123')
        ticket.refresh_from_db()
        self.assertEqual(ticket.paperclip_issue_id, 'pc-issue-123')

    @patch('services.paperclip_client.requests.post')
    def test_sync_ticket_calls_correct_endpoint(self, mock_post):
        mock_post.return_value.json.return_value = {'id': 'pc-123'}
        mock_post.return_value.status_code = 201

        ticket = Ticket.objects.create(title='Test', description='desc')
        client = PaperclipClient()
        client.sync_ticket(ticket)

        # Verify it called the Paperclip issues endpoint
        call_url = mock_post.call_args[0][0]
        self.assertIn('/issues', call_url)

    @patch('services.paperclip_client.requests.post')
    def test_sync_ticket_raises_on_api_error(self, mock_post):
        mock_post.side_effect = Exception('Paperclip connection refused')
        ticket = Ticket.objects.create(title='Test', description='desc')
        client = PaperclipClient()
        with self.assertRaises(Exception):
            client.sync_ticket(ticket)
```

- [ ] **Step 5.2: Run — verify FAIL**

```bash
python manage.py test services.tests.test_paperclip_client -v 2
```

Expected: `ModuleNotFoundError: No module named 'services.paperclip_client'`

- [ ] **Step 5.3: Wiganz implements PaperclipClient**

> 🎯 **Ruach-El:** "What data does Paperclip need to create an issue? Look at spec-0 §6.4 for the API shape."
> "Where do we store the `PAPERCLIP_API_URL` and `PAPERCLIP_COMPANY_ID`? Why env vars and not hardcoded?"

```python
# services/paperclip_client.py
# Wiganz implements this guided by Ruach-El's questions
```

Expected final shape:
```python
import os
import requests
from core.models import Ticket

class PaperclipClient:
    def __init__(self):
        self.base_url = os.getenv('PAPERCLIP_API_URL', 'http://localhost:3100/api')
        self.company_id = os.getenv('PAPERCLIP_COMPANY_ID')

    def sync_ticket(self, ticket: Ticket) -> dict:
        url = f"{self.base_url}/companies/{self.company_id}/issues"
        payload = {
            'title': ticket.title,
            'description': ticket.description,
            'priority': ticket.priority,
            'external_id': str(ticket.id),
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        ticket.paperclip_issue_id = data['id']
        ticket.save(update_fields=['paperclip_issue_id'])
        return data
```

- [ ] **Step 5.4: Run — verify PASS**

```bash
python manage.py test services.tests.test_paperclip_client -v 2
```

Expected: `3 tests passed`

- [ ] **Step 5.5: Add "Sync to Paperclip" Django admin action**

```python
# core/admin.py — add to TicketAdmin
from services.paperclip_client import PaperclipClient

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'paperclip_issue_id', 'created_at']
    list_filter = ['status', 'priority']
    actions = ['sync_to_paperclip']

    def sync_to_paperclip(self, request, queryset):
        client = PaperclipClient()
        for ticket in queryset:
            client.sync_ticket(ticket)
        self.message_user(request, f"Synced {queryset.count()} tickets to Paperclip.")
    sync_to_paperclip.short_description = "Sync selected tickets to Paperclip"
```

- [ ] **Step 5.6: Commit**

```bash
git add services/paperclip_client.py services/tests/test_paperclip_client.py core/admin.py
git commit -m "feat: PaperclipClient service + sync_ticket + admin action"
```

---

### Task 6: Webhook Endpoints (Paperclip → Django)

**Files:**
- Modify: `core/views.py`
- Modify: `core/urls.py`
- Modify: `core/tests/test_views.py`

> 🎯 **Ruach-El:** Before writing, ask:
> "Who calls these webhook endpoints? (Answer: Paperclip calls Django)"
> "Why is this a POST endpoint and not GET? What is the webhook payload shape?"
> "What should Django do when Paperclip says a ticket's status changed to `needs_approval`?"

- [ ] **Step 6.1: Write failing webhook tests**

```python
# Add to core/tests/test_views.py
from core.models import Ticket, Artifact

class PaperclipWebhookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.ticket = Ticket.objects.create(
            title='Test ticket',
            description='desc',
            paperclip_issue_id='pc-issue-123'
        )

    def test_status_webhook_updates_ticket_status(self):
        payload = {
            'issue_id': 'pc-issue-123',
            'new_status': 'needs_approval'
        }
        response = self.client.post(
            '/api/webhooks/paperclip/status/', payload, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'needs_approval')

    def test_artifact_webhook_creates_artifact_record(self):
        payload = {
            'issue_id': 'pc-issue-123',
            'artifact_type': 'research',
            'title': 'auth-research.md',
            'content': '## Auth Research\nUse JWT tokens with DRF...',
            'agent_name': 'researcher'
        }
        response = self.client.post(
            '/api/webhooks/paperclip/artifact/', payload, format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Artifact.objects.filter(ticket=self.ticket).count(), 1)

    def test_status_webhook_returns_404_for_unknown_issue_id(self):
        payload = {'issue_id': 'pc-nonexistent', 'new_status': 'needs_approval'}
        response = self.client.post(
            '/api/webhooks/paperclip/status/', payload, format='json'
        )
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 6.2: Run — verify FAIL**

```bash
python manage.py test core.tests.test_views.PaperclipWebhookTest -v 2
```

Expected: `404 — /api/webhooks/paperclip/status/ not found`

- [ ] **Step 6.3: Wiganz implements webhook views**

> 🎯 **Ruach-El:** "What DRF view type makes sense here? ModelViewSet, APIView, or @api_view? Why?"
> "For the status webhook, what's the minimal thing we need to do? (find ticket by paperclip_issue_id → update status)"

Expected final shape (views.py additions):
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.models import Ticket, Artifact

@api_view(['POST'])
def paperclip_status_webhook(request):
    issue_id = request.data.get('issue_id')
    new_status = request.data.get('new_status')
    ticket = get_object_or_404(Ticket, paperclip_issue_id=issue_id)
    ticket.status = new_status
    ticket.save(update_fields=['status', 'updated_at'])
    return Response({'status': 'updated', 'ticket_id': str(ticket.id)})

@api_view(['POST'])
def paperclip_artifact_webhook(request):
    issue_id = request.data.get('issue_id')
    ticket = get_object_or_404(Ticket, paperclip_issue_id=issue_id)
    artifact = Artifact.objects.create(
        ticket=ticket,
        artifact_type=request.data.get('artifact_type'),
        title=request.data.get('title'),
        content=request.data.get('content'),
        agent_name=request.data.get('agent_name'),
    )
    return Response({'artifact_id': str(artifact.id)}, status=201)
```

Add to `core/urls.py`:
```python
from core.views import TicketViewSet, paperclip_status_webhook, paperclip_artifact_webhook

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/paperclip/status/', paperclip_status_webhook),
    path('webhooks/paperclip/artifact/', paperclip_artifact_webhook),
]
```

- [ ] **Step 6.4: Run all tests — verify PASS**

```bash
python manage.py test core.tests -v 2
```

Expected: `22 tests passed`

- [ ] **Step 6.5: Commit**

```bash
git add core/views.py core/urls.py core/tests/test_views.py
git commit -m "feat: Paperclip webhook handlers for status and artifact"
```

---

### Task 7: Celery Setup + Telegram Notification

**Files:**
- Create: `sdlc_spike/celery.py`
- Create: `services/telegram_notifier.py`
- Create: `services/tests/test_telegram.py`
- Modify: `sdlc_spike/__init__.py`

> 🎯 **Ruach-El:** STOP — teach Celery before writing a single line.
> "Django processes a request and returns a response. What happens if sending a Telegram message takes 3 seconds? Who is waiting?"
> "What is Celery? What is a worker? What is a broker? Draw the flow: Django → Redis → Celery worker → Telegram"
> "Why Redis specifically as the broker and not PostgreSQL?"
> Do NOT proceed until Wiganz can draw the flow on paper.

- [ ] **Step 7.1: Configure Celery app**

```python
# sdlc_spike/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sdlc_spike.settings')
app = Celery('sdlc_spike')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

```python
# sdlc_spike/__init__.py
from .celery import app as celery_app
__all__ = ('celery_app',)
```

- [ ] **Step 7.2: Write failing Telegram test**

```python
# services/tests/test_telegram.py
from unittest.mock import patch, MagicMock, AsyncMock
from django.test import TestCase
from services.telegram_notifier import send_notification

class TelegramNotifierTest(TestCase):
    @patch('services.telegram_notifier.requests.post')
    def test_send_notification_calls_telegram_api(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'ok': True}

        send_notification('Test message: spike is working!')

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('text', str(call_args))

    @patch('services.telegram_notifier.requests.post')
    def test_send_notification_includes_message_text(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'ok': True}

        send_notification('Hello from SDLC Spike!')

        call_kwargs = mock_post.call_args[1]
        self.assertIn('Hello from SDLC Spike!', str(call_kwargs))
```

- [ ] **Step 7.3: Run — verify FAIL**

```bash
python manage.py test services.tests.test_telegram -v 2
```

Expected: `ModuleNotFoundError: No module named 'services.telegram_notifier'`

- [ ] **Step 7.4: Wiganz implements send_notification()**

> 🎯 **Ruach-El:** "Telegram's Bot API uses a simple HTTP POST. The URL format is `https://api.telegram.org/bot{TOKEN}/sendMessage`. What do we need in the request body?"

```python
# services/telegram_notifier.py
# Wiganz implements this guided by Ruach-El's questions
```

Expected final shape:
```python
import os
import requests

def send_notification(message: str) -> bool:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={'chat_id': chat_id, 'text': message}, timeout=10)
    return response.status_code == 200
```

- [ ] **Step 7.5: Run — verify PASS**

```bash
python manage.py test services.tests.test_telegram -v 2
```

Expected: `2 tests passed`

- [ ] **Step 7.6: Wire webhook to trigger Telegram on needs_approval**

Update `paperclip_status_webhook` in `core/views.py`:
```python
from services.telegram_notifier import send_notification

@api_view(['POST'])
def paperclip_status_webhook(request):
    issue_id = request.data.get('issue_id')
    new_status = request.data.get('new_status')
    ticket = get_object_or_404(Ticket, paperclip_issue_id=issue_id)
    ticket.status = new_status
    ticket.save(update_fields=['status', 'updated_at'])

    if new_status == 'needs_approval':
        send_notification(
            f"RESEARCH COMPLETE\n\nTicket: {ticket.title}\n"
            f"Status: needs_approval\n\nReview and approve in Paperclip:\nhttp://localhost:3100"
        )
    return Response({'status': 'updated', 'ticket_id': str(ticket.id)})
```

- [ ] **Step 7.7: Run all tests — verify PASS**

```bash
python manage.py test -v 2
```

Expected: `24 tests passed`

- [ ] **Step 7.8: Commit**

```bash
git add sdlc_spike/celery.py sdlc_spike/__init__.py services/telegram_notifier.py services/tests/test_telegram.py core/views.py
git commit -m "feat: Celery config + Telegram notification on needs_approval status"
```

---

### Day 2 Done Gate

**Before moving to Day 3, ALL of these must be true:**

- [ ] All tests passing: `python manage.py test -v 2`
- [ ] Can create ticket in Django admin → select it → "Sync to Paperclip" action → `paperclip_issue_id` gets set
- [ ] Can POST to `/api/webhooks/paperclip/status/` → ticket status updates in Django
- [ ] Can POST to `/api/webhooks/paperclip/artifact/` → Artifact record created in Django
- [ ] Telegram `send_notification()` is implemented and tested
- [ ] Paperclip installed locally: `npx paperclipai onboard --yes` runs without errors

---

## DAY 3: End-to-End Validation + Go/No-Go

```
╔══════════════════════════════════════════════════════════════╗
║  🧪  SDLC — Phase 7: Day 3 — Spike Validation               ║
║  Goal: Full loop runs with real ticket. 7 criteria scored.   ║
║  Done when: SPIKE_RESULTS.md complete. Go/No-Go decided.     ║
╚══════════════════════════════════════════════════════════════╝
```

> **Ruach-El teaching note — BEFORE Day 3:**
> Ask Wiganz: "What is an integration test vs a unit test? Why do we mock in unit tests but NOT in integration tests?"
> Ask: "What is the 'test ticket' we're using? What is its title? Why use a specific, defined ticket?"
> Ask: "What does 'Go/No-Go' mean in an engineering context? What happens in each case?"

---

### Task 8: End-to-End Integration Test

**Files:**
- Create: `core/tests/test_e2e.py`

> 🎯 **Ruach-El:** "What's the full flow we're testing? Describe it step by step before we write a line."
> "Why do we mock Paperclip and Telegram even in the e2e test? (Answer: the e2e test tests OUR system, not Paperclip's system)"

- [ ] **Step 8.1: Write the E2E test**

```python
# core/tests/test_e2e.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from core.models import Ticket, Artifact, AgentRun
from services.paperclip_client import PaperclipClient

class SpikeEndToEndTest(TestCase):
    """
    Tests the full spike pipeline with mocked external services.
    Validates: create ticket → sync → artifact → status change → Telegram notification.
    """

    @patch('services.telegram_notifier.requests.post')
    @patch('services.paperclip_client.requests.post')
    def test_full_spike_pipeline(self, mock_paperclip_post, mock_telegram_post):
        api = APIClient()

        # 1. Create ticket via API
        mock_paperclip_post.return_value.json.return_value = {'id': 'pc-e2e-999'}
        mock_paperclip_post.return_value.status_code = 201
        mock_telegram_post.return_value.status_code = 200
        mock_telegram_post.return_value.json.return_value = {'ok': True}

        create_response = api.post('/api/tickets/', {
            'title': 'Add user authentication endpoint',
            'description': 'Create JWT auth with DRF. Include rate limiting.',
        }, format='json')
        self.assertEqual(create_response.status_code, 201)
        ticket_id = create_response.data['id']

        # 2. Sync ticket to Paperclip
        ticket = Ticket.objects.get(id=ticket_id)
        client = PaperclipClient()
        client.sync_ticket(ticket)
        ticket.refresh_from_db()
        self.assertEqual(ticket.paperclip_issue_id, 'pc-e2e-999')

        # 3. Paperclip fires artifact webhook (research complete)
        artifact_response = api.post('/api/webhooks/paperclip/artifact/', {
            'issue_id': 'pc-e2e-999',
            'artifact_type': 'research',
            'title': 'auth-research.md',
            'content': '## Auth Research\n\nRecommend JWT with djangorestframework-simplejwt...',
            'agent_name': 'researcher'
        }, format='json')
        self.assertEqual(artifact_response.status_code, 201)
        self.assertEqual(Artifact.objects.filter(ticket=ticket).count(), 1)

        # 4. Paperclip fires status webhook (needs approval)
        status_response = api.post('/api/webhooks/paperclip/status/', {
            'issue_id': 'pc-e2e-999',
            'new_status': 'needs_approval'
        }, format='json')
        self.assertEqual(status_response.status_code, 200)

        # 5. Verify Django state is correct
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'needs_approval')

        # 6. Verify Telegram was notified
        mock_telegram_post.assert_called_once()
        call_body = mock_telegram_post.call_args[1]['json']
        self.assertIn('RESEARCH COMPLETE', call_body['text'])

    def test_ticket_not_found_returns_404(self):
        api = APIClient()
        response = api.post('/api/webhooks/paperclip/status/', {
            'issue_id': 'nonexistent-id',
            'new_status': 'needs_approval'
        }, format='json')
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 8.2: Run — verify PASS**

```bash
python manage.py test core.tests.test_e2e -v 2
```

Expected: `2 tests passed`

- [ ] **Step 8.3: Run ALL tests — final check**

```bash
python manage.py test -v 2
```

Expected: All tests passing.

- [ ] **Step 8.4: Commit**

```bash
git add core/tests/test_e2e.py
git commit -m "feat: end-to-end spike pipeline test"
```

---

### Task 9: Real End-to-End with Live Paperclip

> 🎯 **Ruach-El:** "Now we run the real thing. No mocks. Real Paperclip. Real agents. Real Telegram."
> Before starting: "What are the 7 Go/No-Go criteria? Run through them out loud."

- [ ] **Step 9.1: Start all services**

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery worker
celery -A sdlc_spike worker --loglevel=info

# Terminal 3: Django
python manage.py runserver

# Terminal 4: Paperclip
npx paperclipai onboard --yes
# Visit http://localhost:3100 — set up company "SDLC Spike"
# Create Research agent + Builder agent (see spec-0 §6.2 for config)
```

- [ ] **Step 9.2: Run the test ticket**

Use the exact ticket from the spec:
- **Title:** `Add user authentication endpoint`
- **Description:** `Create a REST API endpoint for user registration and login. Use Django REST Framework with JWT tokens. Include email validation, password hashing, and rate limiting.`
- **Priority:** `high`

1. Create ticket in Django admin (`localhost:8000/admin/`)
2. Select it → "Sync to Paperclip" admin action
3. Verify it appears in Paperclip dashboard (`localhost:3100`)
4. Trigger Research agent heartbeat in Paperclip
5. Wait for research to complete
6. Verify: Telegram notification received?
7. Verify: Artifact saved in Django admin?
8. Approve in Paperclip dashboard
9. Verify: Builder agent runs → code committed → PR opened
10. Verify: GitHub Actions triggers → tests run

- [ ] **Step 9.3: Score the 7 Go/No-Go criteria**

Open `SPIKE_RESULTS.md` and fill in every score + pain point:

```markdown
# Spike Results — 2026-05-07

## Go/No-Go Scores

| # | Criterion | Score | Notes |
|---|-----------|-------|-------|
| 1 | Paperclip installs cleanly | 🟢/🔴 | |
| 2 | Paperclip API works reliably | 🟢/🔴 | |
| 3 | Agent runtime adapter works | 🟢/🔴 | |
| 4 | Execution locks are reliable | 🟢/🔴 | |
| 5 | Approval gates work | 🟢/🔴 | |
| 6 | Status sync works | 🟢/🔴 | |
| 7 | Developer experience | 🟢/🔴 | |

**Total greens:** ___ / 7

**Decision:** GO (5+ greens → Spec 1) / NO-GO (3+ reds → pivot)

## Pain Points
- 

## Bugs Encountered
- 

## Workarounds Used
-

## What Works Well
-
```

- [ ] **Step 9.4: Final commit**

```bash
git add SPIKE_RESULTS.md
git commit -m "feat: spike complete — SPIKE_RESULTS.md with Go/No-Go decision"
```

---

### Spike Done Gate (Final Checklist)

- [ ] Ticket created in Django admin → appears in Paperclip dashboard
- [ ] Research agent produces markdown artifact stored in Django PostgreSQL
- [ ] Telegram notification received when research is complete
- [ ] You can approve in Paperclip dashboard
- [ ] Builder agent runs after approval, commits to feature branch
- [ ] PR opened on GitHub with agent's code
- [ ] GitHub Actions triggers on PR, tests run, results posted as PR comment
- [ ] AgentRun records exist in Django with duration, cost, and artifacts
- [ ] `SPIKE_RESULTS.md` complete with all 7 scores + pain points
- [ ] Go/No-Go decision documented

---

## Self-Review Against Spec

| Spec-0 Requirement | Covered In |
|---|---|
| Ticket model (UUID, status, priority, paperclip_issue_id) | Task 2 |
| Artifact model (FK to Ticket, artifact_type, content, agent_name) | Task 3 |
| AgentRun model (prompt_tokens, completion_tokens, cost, duration) | Task 3 |
| All 3 models in Django admin with list_display | Task 3 |
| GET /api/tickets/ | Task 4 |
| POST /api/tickets/ | Task 4 |
| POST /api/tickets/{id}/sync/ (via admin action) | Task 5 |
| POST /api/webhooks/paperclip/status/ | Task 6 |
| POST /api/webhooks/paperclip/artifact/ | Task 6 |
| PaperclipClient service class (reusable in Spec 1) | Task 5 |
| Celery configuration | Task 7 |
| Telegram notification on needs_approval | Task 7 |
| End-to-end mocked pipeline test | Task 8 |
| Real end-to-end with live Paperclip | Task 9 |
| Go/No-Go scoring (7 criteria) | Task 9 |
| SPIKE_RESULTS.md | Task 9 |

✅ All spike requirements covered.

---

## How to Use This Plan

> **Every session starts here:**
> 1. Read ALL 4 docs (spec, plans, sdlc-thinking-guide, vertical-slices-guide)
> 2. Find the first unchecked `- [ ]` — that is your starting point
> 3. Ruach-El calls the Day banner at the top of the current Day
> 4. Ruach-El asks the teaching questions in the `> 🎯 **Ruach-El:**` callouts
> 5. Wiganz types every line of code — no copy-paste
> 6. Check off completed steps as you go
> 7. Never start the next Day until the current Day's done gate passes

**Reference:**
- Spec: `docs/superpowers/specs/2026-05-07-mas-sdlc-spec-0.md`
- SDLC guide: `docs/learning-guides/sdlc-thinking-guide.md`
- Vertical slices: `docs/learning-guides/vertical-slices-guide.md`
