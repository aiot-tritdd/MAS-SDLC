# QuantApp Implementation Plan

> **For Wiganz + Hadriel sessions:** This is the roadmap. Do NOT execute this alone.
> Every task is done together: Wiganz writes the code, Hadriel teaches the reasoning.
>
> **REQUIRED: Read ALL 4 docs before starting any session:**
> 1. `docs/superpowers/specs/2026-04-15-quant-app-design.md` — scope, models, UI aesthetic, SDLC contract
> 2. `docs/superpowers/plans/2026-04-15-quant-app-plan.md` — this file, find the first unchecked `- [ ]`
> 3. `docs/learning-guides/sdlc-thinking-guide.md` — how to teach each SDLC phase Socratically
> 4. `docs/learning-guides/vertical-slices-guide.md` — vertical slice mindset, done gates, execution loop

**Goal:** Build a stock portfolio tracker (QuantApp) with Golden/Death Cross signals — full stack, fully deployed, fully understood.

**Architecture:** Vertical slices — one complete feature (DB → API → UI → tested) before moving to the next. Schema designed first before any code. React fetches from Django; Django is the only caller of Alpha Vantage.

**Tech Stack:** Django 4.2 + DRF 3.14, React 18 + Vite, TailwindCSS, TanStack Query, PostgreSQL, Alpha Vantage API, Railway (backend), Vercel (frontend)

**Build order:** Setup → Slice 1 (Stocks) → Slice 2 (Portfolio) → Slice 3 (Transactions) → Slice 4 (Signals) → Deploy

---

## File Structure (Everything That Will Exist)

```
quant-app/
├── backend/                          ← Django project root
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                          ← never committed
│   ├── .env.example                  ← committed, no real values
│   ├── Procfile                      ← Railway deploy config
│   ├── quant_app/                    ← Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── stocks/                       ← single Django app (all models here)
│       ├── models.py                 ← Stock, Portfolio, Transaction
│       ├── serializers.py            ← StockSerializer, PortfolioSerializer, TransactionSerializer
│       ├── views.py                  ← StockViewSet, PortfolioViewSet, TransactionViewSet
│       ├── urls.py                   ← DRF Router registration
│       ├── services.py               ← Alpha Vantage calls, MA calculation logic
│       ├── admin.py                  ← Register models for Django admin
│       └── tests/
│           ├── __init__.py
│           ├── test_models.py        ← Unit tests for model properties
│           ├── test_services.py      ← Tests for Alpha Vantage + MA logic
│           └── test_views.py         ← API endpoint integration tests
│
└── frontend/                         ← React project root
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── index.html
    ├── .env                          ← never committed
    ├── .env.example                  ← VITE_API_URL placeholder
    └── src/
        ├── main.jsx                  ← React + TanStack Query provider setup
        ├── App.jsx                   ← Root component, layout shell
        ├── index.css                 ← CSS variables (design system tokens)
        ├── api/
        │   └── client.js             ← axios instance with base URL
        ├── hooks/
        │   ├── useStocks.js          ← useQuery hooks for stocks
        │   ├── usePortfolio.js       ← useQuery hook for portfolio
        │   └── useTransactions.js    ← useQuery + useMutation for transactions
        └── components/
            ├── MetricStrip.jsx       ← Top 3 glow cards (value, P&L, daily)
            ├── PortfolioCard.jsx     ← Donut ring + portfolio summary
            ├── HoldingsLedger.jsx    ← Full holdings table with signal badges
            ├── SignalBadge.jsx       ← Reusable Golden/Death/Neutral badge
            ├── SignalPanel.jsx       ← MA50/MA200 analysis panel
            ├── TransactionForm.jsx   ← Buy/sell form
            └── TransactionHistory.jsx ← Scrollable transaction list
```

---

## PHASE 0: Project Setup

```
╔══════════════════════════════════════════════════════╗
║  ⚙️  SDLC — Phase 5 Prep: Project Setup             ║
║  Goal: Both projects running locally before any code ║
╚══════════════════════════════════════════════════════╝
```

> **Hadriel teaching note:** Before each setup step, ask Wiganz WHY each config file or
> environment variable exists. Never let setup be mindless copy-paste.

---

### Task 1: Django Backend Setup

**Files:**
- Create: `backend/` (project root)
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/quant_app/settings.py`
- Create: `backend/quant_app/urls.py`

- [ ] **Step 1.1: Create project structure**

```bash
mkdir quant-app && cd quant-app
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate        # Mac/Linux
pip install django djangorestframework psycopg2-binary python-dotenv requests django-cors-headers
pip freeze > requirements.txt
django-admin startproject quant_app .
python manage.py startapp stocks
```

- [ ] **Step 1.2: Create `.env` file**

```bash
# backend/.env  (NEVER commit this)
SECRET_KEY=your-local-dev-secret-key-change-in-production
DEBUG=True
DATABASE_URL=postgres://postgres:postgres@localhost:5432/quantapp
ALPHA_VANTAGE_KEY=your_key_here
```

```bash
# backend/.env.example  (DO commit this — no real values)
SECRET_KEY=
DEBUG=True
DATABASE_URL=
ALPHA_VANTAGE_KEY=
```

- [ ] **Step 1.3: Configure `settings.py`**

```python
# backend/quant_app/settings.py
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
    'corsheaders',
    'stocks',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',   # must be first
    'django.middleware.security.SecurityMiddleware',
    # ... rest of default middleware
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',   # Vite dev server
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'quantapp',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]
}
```

- [ ] **Step 1.4: Configure root URLs**

```python
# backend/quant_app/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('stocks.urls')),
]
```

- [ ] **Step 1.5: Create local PostgreSQL database**

```bash
createdb quantapp
# or via psql: CREATE DATABASE quantapp;
```

- [ ] **Step 1.6: Verify Django runs**

```bash
python manage.py migrate
python manage.py runserver
```

Expected: `Starting development server at http://127.0.0.1:8000/`
Visit `http://127.0.0.1:8000/api/` — should return DRF browsable API root.

- [ ] **Step 1.7: Initial commit**

```bash
cd ..  # back to quant-app root
git init
echo "backend/venv/" >> .gitignore
echo "backend/.env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
git add .
git commit -m "chore: initial Django project setup"
```

---

### Task 2: React Frontend Setup

**Files:**
- Create: `frontend/` (Vite project)
- Create: `frontend/src/index.css`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/api/client.js`

- [ ] **Step 2.1: Create React + Vite project**

```bash
# from quant-app root
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install @tanstack/react-query axios recharts
```

- [ ] **Step 2.2: Configure TailwindCSS**

```javascript
// frontend/tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

- [ ] **Step 2.3: Set up design system CSS variables**

```css
/* frontend/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg-primary:   #0D0D0D;
  --bg-surface:   #141414;
  --bg-elevated:  #1a1a1a;
  --bg-border:    #2a2a2a;
  --accent-gold:  #e8820a;
  --accent-green: #22c55e;
  --accent-red:   #ef4444;
  --accent-blue:  #3b82f6;
  --text-primary: #f5f5f5;
  --text-muted:   #6b7280;
  --text-dim:     #4b5563;
  --glow-gold:    0 0 20px rgba(232, 130, 10, 0.3);
  --glow-green:   0 0 20px rgba(34, 197, 94, 0.2);
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', system-ui, sans-serif;
}
```

- [ ] **Step 2.4: Create `.env` file**

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
```

```bash
# frontend/.env.example
VITE_API_URL=
```

- [ ] **Step 2.5: Create axios client**

```javascript
// frontend/src/api/client.js
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
})

export default client
```

- [ ] **Step 2.6: Set up TanStack Query provider**

```jsx
// frontend/src/main.jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.jsx'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 30_000 },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
)
```

- [ ] **Step 2.7: Verify React runs**

```bash
npm run dev
```

Expected: `Local: http://localhost:5173/`
Browser shows Vite default page with dark background.

- [ ] **Step 2.8: Commit**

```bash
cd ..  # quant-app root
echo "frontend/node_modules/" >> .gitignore
echo "frontend/.env" >> .gitignore
echo "frontend/dist/" >> .gitignore
git add .
git commit -m "chore: React + Vite + TailwindCSS + TanStack Query setup"
```

---

## SLICE 1: Stocks Feature

```
╔══════════════════════════════════════════════════════════╗
║  🗄️  SDLC Phase 4 → 5 → 6: Stocks Vertical Slice        ║
║  DB: Stock table                                         ║
║  API: GET /api/stocks/ + POST /api/stocks/<t>/fetch/     ║
║  UI: StockList + price refresh button                    ║
║  Done when: Can see stocks on screen, refresh real price ║
╚══════════════════════════════════════════════════════════╝
```

> **Hadriel teaching note — BEFORE this slice:**
> Ask Wiganz: "What fields does a Stock need? Why is `current_price` nullable?"
> Ask: "What does `unique=True` on ticker actually enforce in the database?"
> Do NOT proceed until Wiganz can explain each field and why it exists.

---

### Task 3: Stock Model + Migration

**Files:**
- Modify: `backend/stocks/models.py`
- Create: `backend/stocks/tests/test_models.py`

- [ ] **Step 3.1: Write the failing test first**

```python
# backend/stocks/tests/test_models.py
from django.test import TestCase
from stocks.models import Stock
from decimal import Decimal

class StockModelTest(TestCase):
    def test_stock_str_returns_ticker(self):
        stock = Stock.objects.create(ticker='AAPL', name='Apple Inc.')
        self.assertEqual(str(stock), 'AAPL')

    def test_ticker_is_unique(self):
        Stock.objects.create(ticker='AAPL', name='Apple Inc.')
        with self.assertRaises(Exception):
            Stock.objects.create(ticker='AAPL', name='Apple Duplicate')

    def test_current_price_can_be_null(self):
        stock = Stock.objects.create(ticker='TSLA', name='Tesla')
        self.assertIsNone(stock.current_price)
```

- [ ] **Step 3.2: Run tests — verify they fail**

```bash
cd backend
python manage.py test stocks.tests.test_models -v 2
```

Expected: `ERROR — stocks.models has no attribute Stock`

- [ ] **Step 3.3: Wiganz implements the Stock model**

> 🎯 **Hadriel:** Ask "What Django field type stores money/prices? Why NOT FloatField?"
> Guide Wiganz to discover DecimalField and the floating-point precision issue.
> Ask "What does auto_now=True do vs auto_now_add=True?"

```python
# backend/stocks/models.py
from django.db import models

class Stock(models.Model):
    # Wiganz implements this guided by Hadriel's questions
    pass
```

Expected final shape:
```python
class Stock(models.Model):
    ticker        = models.CharField(max_length=10, unique=True)
    name          = models.CharField(max_length=200)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_updated  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker
```

- [ ] **Step 3.4: Create and run migration**

```bash
python manage.py makemigrations stocks
python manage.py migrate
```

Expected: `Created model Stock`

- [ ] **Step 3.5: Run tests — verify they pass**

```bash
python manage.py test stocks.tests.test_models -v 2
```

Expected: `3 tests passed`

- [ ] **Step 3.6: Register in admin**

```python
# backend/stocks/admin.py
from django.contrib import admin
from .models import Stock

admin.site.register(Stock)
```

- [ ] **Step 3.7: Commit**

```bash
git add backend/stocks/models.py backend/stocks/tests/ backend/stocks/admin.py backend/stocks/migrations/
git commit -m "feat: Stock model with ticker, name, current_price, last_updated"
```

---

### Task 4: Stock Serializer + ViewSet + URL

**Files:**
- Create: `backend/stocks/serializers.py`
- Modify: `backend/stocks/views.py`
- Create: `backend/stocks/urls.py`
- Create: `backend/stocks/tests/test_views.py`

- [ ] **Step 4.1: Write the failing API test**

```python
# backend/stocks/tests/test_views.py
from django.test import TestCase
from rest_framework.test import APIClient
from stocks.models import Stock
from decimal import Decimal

class StockListAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Stock.objects.create(ticker='AAPL', name='Apple Inc.', current_price=Decimal('185.00'))
        Stock.objects.create(ticker='NVDA', name='NVIDIA', current_price=Decimal('576.00'))

    def test_list_stocks_returns_200(self):
        response = self.client.get('/api/stocks/')
        self.assertEqual(response.status_code, 200)

    def test_list_stocks_returns_correct_fields(self):
        response = self.client.get('/api/stocks/')
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertIn('ticker', data[0])
        self.assertIn('name', data[0])
        self.assertIn('current_price', data[0])
        self.assertIn('last_updated', data[0])

    def test_list_stocks_returns_correct_data(self):
        response = self.client.get('/api/stocks/')
        tickers = [s['ticker'] for s in response.json()]
        self.assertIn('AAPL', tickers)
        self.assertIn('NVDA', tickers)
```

- [ ] **Step 4.2: Run tests — verify they fail**

```bash
python manage.py test stocks.tests.test_views -v 2
```

Expected: `404 NOT FOUND — /api/stocks/ not registered`

- [ ] **Step 4.3: Wiganz implements StockSerializer**

> 🎯 **Hadriel:** Ask "What is a serializer actually doing? Why can't we send a Django model directly to React?"
> Ask "What's the difference between `fields = '__all__'` and listing fields explicitly?"
> Guide discovery: listing fields explicitly = you control exactly what the API exposes.

```python
# backend/stocks/serializers.py
from rest_framework import serializers
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'ticker', 'name', 'current_price', 'last_updated']
```

- [ ] **Step 4.4: Wiganz implements StockViewSet**

> 🎯 **Hadriel:** Ask "Why ModelViewSet instead of a plain function view?"
> Ask "What does `queryset` and `serializer_class` do in a ViewSet?"
> Ask "What HTTP methods does ModelViewSet give us for free?"

```python
# backend/stocks/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Stock
from .serializers import StockSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    http_method_names = ['get']   # read-only for now — fetch action added in Task 5
```

- [ ] **Step 4.5: Wiganz registers the URL with DRF Router**

> 🎯 **Hadriel:** Ask "What does a DRF Router do? What URLs does it generate?"
> Show them the router generates: `/api/stocks/` and `/api/stocks/<pk>/`

```python
# backend/stocks/urls.py
from rest_framework.routers import DefaultRouter
from .views import StockViewSet

router = DefaultRouter()
router.register(r'stocks', StockViewSet, basename='stock')

urlpatterns = router.urls
```

- [ ] **Step 4.6: Run tests — verify they pass**

```bash
python manage.py test stocks.tests.test_views -v 2
```

Expected: `3 tests passed`

- [ ] **Step 4.7: Manually verify in browser**

```bash
python manage.py runserver
# Visit: http://localhost:8000/api/stocks/
```

Expected: DRF browsable API showing empty list `[]`
Create a stock via Django admin, refresh — should appear.

- [ ] **Step 4.8: Commit**

```bash
git add backend/stocks/serializers.py backend/stocks/views.py backend/stocks/urls.py backend/stocks/tests/test_views.py
git commit -m "feat: Stock serializer, viewset, and /api/stocks/ endpoint"
```

---

### Task 5: Alpha Vantage Service + Fetch Action

**Files:**
- Create: `backend/stocks/services.py`
- Modify: `backend/stocks/views.py`
- Create: `backend/stocks/tests/test_services.py`

- [ ] **Step 5.1: Write the failing service test (with mock)**

```python
# backend/stocks/tests/test_services.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from stocks.models import Stock
from stocks import services
from decimal import Decimal

class AlphaVantageServiceTest(TestCase):
    @patch('stocks.services.requests.get')
    def test_fetch_stock_price_updates_model(self, mock_get):
        # Arrange: mock Alpha Vantage response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'Global Quote': {
                '05. price': '185.40',
                '01. symbol': 'AAPL',
            }
        }
        mock_get.return_value = mock_response

        stock = Stock.objects.create(ticker='AAPL', name='Apple Inc.')

        # Act
        result = services.fetch_stock_price('AAPL')

        # Assert
        stock.refresh_from_db()
        self.assertEqual(stock.current_price, Decimal('185.40'))
        self.assertEqual(result['ticker'], 'AAPL')
        self.assertEqual(result['current_price'], Decimal('185.40'))

    @patch('stocks.services.requests.get')
    def test_fetch_stock_price_handles_api_error(self, mock_get):
        mock_get.side_effect = Exception('API down')
        Stock.objects.create(ticker='AAPL', name='Apple Inc.')
        with self.assertRaises(Exception):
            services.fetch_stock_price('AAPL')
```

- [ ] **Step 5.2: Run tests — verify they fail**

```bash
python manage.py test stocks.tests.test_services -v 2
```

Expected: `ImportError — stocks.services not found`

- [ ] **Step 5.3: Wiganz implements the Alpha Vantage service**

> 🎯 **Hadriel:** Ask "Why does this logic live in `services.py` and NOT in `views.py`?"
> Key insight: Views handle HTTP. Services handle business logic. Separation of concerns.
> Ask "Why do we save to DB immediately after fetching?" (caching + rate limit protection)

```python
# backend/stocks/services.py
import os
import requests
from decimal import Decimal
from .models import Stock

def fetch_stock_price(ticker: str) -> dict:
    """
    Fetch current price from Alpha Vantage and cache in DB.
    Returns dict with ticker and current_price.
    Raises Exception if API call fails.
    """
    api_key = os.getenv('ALPHA_VANTAGE_KEY')
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': ticker,
        'apikey': api_key,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    price_str = data['Global Quote']['05. price']
    price = Decimal(price_str)

    # Cache immediately in DB — never waste a rate-limited API call
    stock = Stock.objects.get(ticker=ticker)
    stock.current_price = price
    stock.save()

    return {'ticker': ticker, 'current_price': price}
```

- [ ] **Step 5.4: Add fetch custom action to StockViewSet**

> 🎯 **Hadriel:** Ask "What is `@action` in DRF? How is it different from a regular ViewSet method?"
> Ask "Why `detail=True`? What URL does that generate?"

```python
# backend/stocks/views.py  (updated)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Stock
from .serializers import StockSerializer
from . import services

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    http_method_names = ['get', 'post']
    lookup_field = 'ticker'

    @action(detail=True, methods=['post'], url_path='fetch')
    def fetch_price(self, request, ticker=None):
        """POST /api/stocks/<ticker>/fetch/ — triggers Alpha Vantage call"""
        try:
            result = services.fetch_stock_price(ticker)
            return Response(result, status=status.HTTP_200_OK)
        except Stock.DoesNotExist:
            return Response({'error': f'Stock {ticker} not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
```

- [ ] **Step 5.5: Run all backend tests**

```bash
python manage.py test stocks -v 2
```

Expected: All tests pass (models + views + services)

- [ ] **Step 5.6: Commit**

```bash
git add backend/stocks/services.py backend/stocks/views.py backend/stocks/tests/test_services.py
git commit -m "feat: Alpha Vantage service + /api/stocks/<ticker>/fetch/ action"
```

---

### Task 6: React Stocks Component

**Files:**
- Modify: `frontend/src/App.jsx`
- Create: `frontend/src/hooks/useStocks.js`
- Create: `frontend/src/components/HoldingsLedger.jsx` (stub — full version in Slice 2)

- [ ] **Step 6.1: Create the stocks data hook**

> 🎯 **Hadriel:** Ask "What is TanStack Query's `useQuery`? What problem does it solve over `useEffect + fetch`?"
> Ask "What is `queryKey`? Why is it an array?"

```javascript
// frontend/src/hooks/useStocks.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../api/client'

export function useStocks() {
  return useQuery({
    queryKey: ['stocks'],
    queryFn: () => client.get('/api/stocks/').then(r => r.data),
  })
}

export function useRefreshPrice() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (ticker) => client.post(`/api/stocks/${ticker}/fetch/`),
    onSuccess: () => {
      // Invalidate all queries that depend on stock prices
      queryClient.invalidateQueries({ queryKey: ['stocks'] })
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })
}
```

- [ ] **Step 6.2: Wiganz builds the App shell with dark layout**

> 🎯 **Hadriel:** Ask "What is the top-level layout of this dashboard? What CSS variables do we use for the background?"
> Guide Wiganz to apply `var(--bg-primary)` and the SOVEREIGN aesthetic from the spec.

```jsx
// frontend/src/App.jsx — Wiganz implements the layout shell
// Structure: nav bar + main content area using CSS variables from index.css
```

Expected structure Wiganz arrives at:
```jsx
import { useStocks, useRefreshPrice } from './hooks/useStocks'

export default function App() {
  const { data: stocks, isLoading, isError } = useStocks()
  const refreshPrice = useRefreshPrice()

  if (isLoading) return <div style={{ color: 'var(--text-muted)', padding: '2rem' }}>Loading...</div>
  if (isError)   return <div style={{ color: 'var(--accent-red)', padding: '2rem' }}>Failed to load stocks</div>

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', padding: '2rem' }}>
      <h1 style={{ color: 'var(--accent-gold)', fontFamily: 'monospace' }}>QUANT /</h1>
      <div>
        {stocks?.map(stock => (
          <div key={stock.ticker} style={{ background: 'var(--bg-surface)', padding: '1rem', marginBottom: '0.5rem' }}>
            <span style={{ color: 'var(--text-primary)' }}>{stock.ticker}</span>
            <span style={{ color: 'var(--accent-gold)', marginLeft: '1rem' }}>
              ${stock.current_price ?? '—'}
            </span>
            <button
              onClick={() => refreshPrice.mutate(stock.ticker)}
              style={{ marginLeft: '1rem', color: 'var(--accent-gold)' }}
            >
              Refresh
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 6.3: Seed test data in Django admin**

```bash
cd backend && python manage.py runserver
# Visit http://localhost:8000/admin/
# Create a superuser: python manage.py createsuperuser
# Add stocks: AAPL, NVDA, TSLA, MSFT
```

- [ ] **Step 6.4: Verify Slice 1 is done**

```bash
# Terminal 1: backend
cd backend && python manage.py runserver

# Terminal 2: frontend
cd frontend && npm run dev
```

Open `http://localhost:5173` — you should see stocks listed.
Click "Refresh" on AAPL — price should update from Alpha Vantage.

✅ **Slice 1 done gate:**
- [ ] Stocks list visible in browser with real data
- [ ] Price refresh button hits real Alpha Vantage and updates
- [ ] All backend tests passing
- [ ] Loading and error states handled in React

- [ ] **Step 6.5: Commit**

```bash
git add frontend/src/
git commit -m "feat: Slice 1 complete — stocks list + Alpha Vantage price refresh"
```

---

## SLICE 2: Portfolio Feature

```
╔══════════════════════════════════════════════════════════╗
║  🗄️  SDLC Phase 4 → 5 → 6: Portfolio Vertical Slice     ║
║  DB: Portfolio table (FK → Stock, computed P&L)          ║
║  API: GET /api/portfolio/                                 ║
║  UI: PortfolioCard (donut) + HoldingsLedger table        ║
║  Done when: Can see P&L on screen with real numbers      ║
╚══════════════════════════════════════════════════════════╝
```

> **Hadriel teaching note — BEFORE this slice:**
> Ask "Why is Portfolio a OneToOne to Stock, not a ForeignKey?"
> Ask "If AAPL price changes, should the stored P&L number update automatically? Why not just store it?"
> Don't proceed until Wiganz can explain computed @property vs stored column.

---

### Task 7: Portfolio Model + Migration

**Files:**
- Modify: `backend/stocks/models.py`
- Modify: `backend/stocks/tests/test_models.py`

- [ ] **Step 7.1: Write the failing tests for Portfolio**

```python
# Add to backend/stocks/tests/test_models.py

from stocks.models import Stock, Portfolio
from decimal import Decimal

class PortfolioModelTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            ticker='AAPL', name='Apple Inc.', current_price=Decimal('185.00')
        )

    def test_portfolio_pnl_calculated_correctly(self):
        portfolio = Portfolio.objects.create(
            stock=self.stock, quantity=10, avg_buy_price=Decimal('150.00')
        )
        # pnl = (185 - 150) * 10 = 350
        self.assertEqual(portfolio.pnl, Decimal('350.00'))

    def test_portfolio_pnl_percent_calculated_correctly(self):
        portfolio = Portfolio.objects.create(
            stock=self.stock, quantity=10, avg_buy_price=Decimal('150.00')
        )
        # pnl_percent = (350 / 1500) * 100 = 23.33...
        self.assertAlmostEqual(float(portfolio.pnl_percent), 23.33, places=1)

    def test_portfolio_pnl_is_negative_when_losing(self):
        losing_stock = Stock.objects.create(
            ticker='TSLA', name='Tesla', current_price=Decimal('217.50')
        )
        portfolio = Portfolio.objects.create(
            stock=losing_stock, quantity=8, avg_buy_price=Decimal('240.00')
        )
        # pnl = (217.50 - 240) * 8 = -180
        self.assertEqual(portfolio.pnl, Decimal('-180.00'))

    def test_portfolio_deleted_when_stock_deleted(self):
        Portfolio.objects.create(stock=self.stock, quantity=10, avg_buy_price=Decimal('150.00'))
        self.stock.delete()
        self.assertEqual(Portfolio.objects.count(), 0)
```

- [ ] **Step 7.2: Run tests — verify they fail**

```bash
python manage.py test stocks.tests.test_models -v 2
```

Expected: `ImportError — cannot import Portfolio`

- [ ] **Step 7.3: Wiganz implements Portfolio model**

> 🎯 **Hadriel:** Ask "What is `@property` in Python? How is it different from a regular method?"
> Ask "If we stored pnl as a column, what problem would we have when stock price changes?"

```python
# Add to backend/stocks/models.py

class Portfolio(models.Model):
    # Wiganz implements guided by Hadriel
    pass
```

Expected shape:
```python
class Portfolio(models.Model):
    stock         = models.OneToOneField(Stock, on_delete=models.CASCADE, related_name='portfolio')
    quantity      = models.IntegerField()
    avg_buy_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def pnl(self):
        if self.stock.current_price is None:
            return Decimal('0')
        return (self.stock.current_price - self.avg_buy_price) * self.quantity

    @property
    def pnl_percent(self):
        cost_basis = self.avg_buy_price * self.quantity
        if cost_basis == 0:
            return Decimal('0')
        return (self.pnl / cost_basis) * 100

    def __str__(self):
        return f'{self.stock.ticker} — {self.quantity} shares'
```

- [ ] **Step 7.4: Create and run migration**

```bash
python manage.py makemigrations stocks
python manage.py migrate
```

- [ ] **Step 7.5: Run tests — verify they pass**

```bash
python manage.py test stocks.tests.test_models -v 2
```

Expected: All tests pass (Stock tests + Portfolio tests)

- [ ] **Step 7.6: Commit**

```bash
git add backend/stocks/models.py backend/stocks/migrations/ backend/stocks/tests/test_models.py
git commit -m "feat: Portfolio model with pnl and pnl_percent computed properties"
```

---

### Task 8: Portfolio Serializer + ViewSet

**Files:**
- Modify: `backend/stocks/serializers.py`
- Modify: `backend/stocks/views.py`
- Modify: `backend/stocks/urls.py`
- Modify: `backend/stocks/tests/test_views.py`

- [ ] **Step 8.1: Write failing API tests for portfolio endpoint**

```python
# Add to backend/stocks/tests/test_views.py

class PortfolioAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        stock = Stock.objects.create(ticker='AAPL', name='Apple Inc.', current_price=Decimal('185.00'))
        Portfolio.objects.create(stock=stock, quantity=10, avg_buy_price=Decimal('150.00'))

    def test_portfolio_returns_200(self):
        response = self.client.get('/api/portfolio/')
        self.assertEqual(response.status_code, 200)

    def test_portfolio_includes_pnl(self):
        response = self.client.get('/api/portfolio/')
        data = response.json()
        holding = data['holdings'][0]
        self.assertIn('pnl', holding)
        self.assertIn('pnl_percent', holding)
        self.assertEqual(Decimal(holding['pnl']), Decimal('350.00'))

    def test_portfolio_includes_total_value(self):
        response = self.client.get('/api/portfolio/')
        data = response.json()
        self.assertIn('total_value', data)
        self.assertIn('total_pnl', data)
```

- [ ] **Step 8.2: Run tests — verify they fail**

```bash
python manage.py test stocks.tests.test_views.PortfolioAPITest -v 2
```

- [ ] **Step 8.3: Wiganz implements PortfolioSerializer**

> 🎯 **Hadriel:** Ask "How do you expose a @property through a DRF serializer?"
> Key concept: `SerializerMethodField` — read-only field computed by a method.
> Ask "Why can't we just use `fields = '__all__'` here?"

```python
# Add to backend/stocks/serializers.py

class PortfolioSerializer(serializers.ModelSerializer):
    ticker        = serializers.CharField(source='stock.ticker', read_only=True)
    name          = serializers.CharField(source='stock.name', read_only=True)
    current_price = serializers.DecimalField(source='stock.current_price', max_digits=10, decimal_places=2, read_only=True)
    pnl           = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    pnl_percent   = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'ticker', 'name', 'quantity', 'avg_buy_price', 'current_price', 'pnl', 'pnl_percent']
```

- [ ] **Step 8.4: Wiganz implements PortfolioViewSet**

> 🎯 **Hadriel:** Ask "How do we compute total_value and total_pnl for the whole portfolio?"
> Guide: iterate holdings in Python, sum up — don't store it.

```python
# Add to backend/stocks/views.py

class PortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Portfolio.objects.select_related('stock').all()
    serializer_class = PortfolioSerializer

    def list(self, request):
        holdings = self.get_queryset()
        serializer = self.get_serializer(holdings, many=True)
        data = serializer.data

        total_value = sum(
            (h.stock.current_price or 0) * h.quantity for h in holdings
        )
        total_pnl = sum(h.pnl for h in holdings)
        cost_basis = sum(h.avg_buy_price * h.quantity for h in holdings)
        total_pnl_percent = (total_pnl / cost_basis * 100) if cost_basis else 0

        return Response({
            'holdings': data,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_percent': round(total_pnl_percent, 2),
        })
```

- [ ] **Step 8.5: Register portfolio URL**

```python
# backend/stocks/urls.py — add:
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')
```

- [ ] **Step 8.6: Run all backend tests**

```bash
python manage.py test stocks -v 2
```

Expected: All tests pass

- [ ] **Step 8.7: Commit**

```bash
git add backend/stocks/
git commit -m "feat: Portfolio serializer, viewset, and /api/portfolio/ endpoint"
```

---

### Task 9: React Portfolio Components

**Files:**
- Create: `frontend/src/hooks/usePortfolio.js`
- Create: `frontend/src/components/MetricStrip.jsx`
- Create: `frontend/src/components/PortfolioCard.jsx`
- Create: `frontend/src/components/HoldingsLedger.jsx`
- Create: `frontend/src/components/SignalBadge.jsx`
- Modify: `frontend/src/App.jsx`

- [ ] **Step 9.1: Create portfolio hook**

```javascript
// frontend/src/hooks/usePortfolio.js
import { useQuery } from '@tanstack/react-query'
import client from '../api/client'

export function usePortfolio() {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: () => client.get('/api/portfolio/').then(r => r.data),
  })
}
```

- [ ] **Step 9.2: Wiganz builds SignalBadge (reusable)**

> 🎯 **Hadriel:** Ask "What are the 3 possible signal values? How do we map each to a color?"
> This is a pure presentational component — no API calls, just props in, UI out.

```jsx
// frontend/src/components/SignalBadge.jsx — Wiganz implements
// Props: signal ('Golden Cross' | 'Death Cross' | 'Neutral' | null)
// Renders: colored badge with signal text
// Uses: var(--accent-green), var(--accent-red), var(--accent-blue) from CSS variables
```

- [ ] **Step 9.3: Wiganz builds HoldingsLedger table**

> 🎯 **Hadriel:** Ask "What columns does the Holdings Ledger need? Reference the demo data in the spec."
> Ask "How do you show positive P&L in green and negative in red dynamically?"

```jsx
// frontend/src/components/HoldingsLedger.jsx — Wiganz implements
// Props: holdings (array), onRefresh (function called with ticker)
// Renders: table with columns: Symbol, Shares, Avg Cost, Current, P&L, Signal
// Uses: SignalBadge component for signal column
```

- [ ] **Step 9.4: Wiganz builds MetricStrip (top 3 glow cards)**

> 🎯 **Hadriel:** Ask "What 3 metrics does the top strip show? Where do those numbers come from?"
> Guide: total_value, total_pnl, total_pnl_percent from portfolio API response.

```jsx
// frontend/src/components/MetricStrip.jsx — Wiganz implements
// Props: totalValue, totalPnl, totalPnlPercent
// Renders: 3 gradient glow cards (VIVID aesthetic from spec)
// CSS: var(--glow-green) or var(--glow-gold) box-shadow based on sign
```

- [ ] **Step 9.5: Wire together in App.jsx**

```jsx
// frontend/src/App.jsx — update to use portfolio data
import { usePortfolio } from './hooks/usePortfolio'
import { useRefreshPrice } from './hooks/useStocks'
import MetricStrip from './components/MetricStrip'
import HoldingsLedger from './components/HoldingsLedger'

export default function App() {
  const { data: portfolio, isLoading, isError } = usePortfolio()
  const refreshPrice = useRefreshPrice()

  if (isLoading) return <div style={{ color: 'var(--text-muted)', padding: '2rem' }}>Loading portfolio...</div>
  if (isError)   return <div style={{ color: 'var(--accent-red)', padding: '2rem' }}>Failed to load portfolio</div>

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', padding: '2rem' }}>
      <header style={{ color: 'var(--accent-gold)', fontFamily: 'monospace', marginBottom: '2rem' }}>
        QUANT /
      </header>
      <MetricStrip
        totalValue={portfolio?.total_value}
        totalPnl={portfolio?.total_pnl}
        totalPnlPercent={portfolio?.total_pnl_percent}
      />
      <HoldingsLedger
        holdings={portfolio?.holdings ?? []}
        onRefresh={(ticker) => refreshPrice.mutate(ticker)}
      />
    </div>
  )
}
```

- [ ] **Step 9.6: Seed Portfolio data in admin**

```bash
# Visit http://localhost:8000/admin/stocks/portfolio/add/
# Add: AAPL 10 shares @ $150, NVDA 5 shares @ $380, TSLA 8 shares @ $240, MSFT 4 shares @ $380
```

- [ ] **Step 9.7: Verify Slice 2 done gate**

✅ **Slice 2 done gate:**
- [ ] Portfolio P&L visible in browser with real numbers
- [ ] Positive P&L shows green, negative shows red
- [ ] Holdings table shows all 4 stocks from demo data
- [ ] Metric strip shows total value, total P&L, total %
- [ ] All backend tests passing

- [ ] **Step 9.8: Commit**

```bash
git add frontend/src/
git commit -m "feat: Slice 2 complete — portfolio P&L, holdings ledger, metric strip"
```

---

## SLICE 3: Transactions Feature

```
╔══════════════════════════════════════════════════════════╗
║  🗄️  SDLC Phase 4 → 5 → 6: Transactions Vertical Slice  ║
║  DB: Transaction table (FK → Stock, buy/sell choices)    ║
║  API: GET /api/transactions/ + POST /api/transactions/   ║
║  UI: TransactionForm + TransactionHistory                ║
║  Done when: Can record a trade and see it in history     ║
╚══════════════════════════════════════════════════════════╝
```

> **Hadriel teaching note — BEFORE this slice:**
> Ask "Why is Transaction a ForeignKey to Stock (not OneToOne like Portfolio)?"
> Ask "What is `choices=` on a CharField? How does Django enforce it?"

---

### Task 10: Transaction Model + Migration

**Files:**
- Modify: `backend/stocks/models.py`
- Modify: `backend/stocks/tests/test_models.py`

- [ ] **Step 10.1: Write failing tests**

```python
# Add to backend/stocks/tests/test_models.py

class TransactionModelTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(ticker='AAPL', name='Apple Inc.', current_price=Decimal('185.00'))

    def test_transaction_created_with_correct_fields(self):
        tx = Transaction.objects.create(
            stock=self.stock, type='buy', price=Decimal('150.00'), quantity=10
        )
        self.assertEqual(tx.type, 'buy')
        self.assertEqual(tx.quantity, 10)
        self.assertIsNotNone(tx.timestamp)

    def test_one_stock_can_have_many_transactions(self):
        Transaction.objects.create(stock=self.stock, type='buy', price=Decimal('150.00'), quantity=5)
        Transaction.objects.create(stock=self.stock, type='buy', price=Decimal('160.00'), quantity=5)
        Transaction.objects.create(stock=self.stock, type='sell', price=Decimal('185.00'), quantity=3)
        self.assertEqual(Transaction.objects.filter(stock=self.stock).count(), 3)

    def test_transactions_deleted_when_stock_deleted(self):
        Transaction.objects.create(stock=self.stock, type='buy', price=Decimal('150.00'), quantity=10)
        self.stock.delete()
        self.assertEqual(Transaction.objects.count(), 0)
```

- [ ] **Step 10.2: Wiganz implements Transaction model**

> 🎯 **Hadriel:** Ask "What does `choices=` on a CharField actually do in Django?"
> Ask "Why `auto_now_add=True` for timestamp instead of `auto_now=True`?"
> Key difference: `auto_now_add` sets once on create. `auto_now` updates on every save.

```python
# Add to backend/stocks/models.py — Wiganz implements
class Transaction(models.Model):
    pass  # Wiganz fills in with Hadriel guiding
```

- [ ] **Step 10.3: Migrate and run tests**

```bash
python manage.py makemigrations && python manage.py migrate
python manage.py test stocks.tests.test_models -v 2
```

- [ ] **Step 10.4: Commit**

```bash
git add backend/stocks/models.py backend/stocks/migrations/ backend/stocks/tests/
git commit -m "feat: Transaction model with buy/sell choices and FK to Stock"
```

---

### Task 11: Transaction Serializer + ViewSet (GET + POST)

**Files:**
- Modify: `backend/stocks/serializers.py`
- Modify: `backend/stocks/views.py`
- Modify: `backend/stocks/urls.py`
- Modify: `backend/stocks/tests/test_views.py`

- [ ] **Step 11.1: Write failing tests**

```python
# Add to backend/stocks/tests/test_views.py

class TransactionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.stock = Stock.objects.create(ticker='AAPL', name='Apple Inc.', current_price=Decimal('185.00'))

    def test_list_transactions_returns_200(self):
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 200)

    def test_create_transaction_returns_201(self):
        payload = {'ticker': 'AAPL', 'type': 'buy', 'price': '150.00', 'quantity': 10}
        response = self.client.post('/api/transactions/', payload, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_transaction_saves_to_db(self):
        payload = {'ticker': 'AAPL', 'type': 'buy', 'price': '150.00', 'quantity': 10}
        self.client.post('/api/transactions/', payload, format='json')
        self.assertEqual(Transaction.objects.count(), 1)

    def test_create_transaction_invalid_type_returns_400(self):
        payload = {'ticker': 'AAPL', 'type': 'hodl', 'price': '150.00', 'quantity': 10}
        response = self.client.post('/api/transactions/', payload, format='json')
        self.assertEqual(response.status_code, 400)
```

- [ ] **Step 11.2: Wiganz implements TransactionSerializer + ViewSet**

> 🎯 **Hadriel:** Ask "For a POST endpoint that creates a transaction, which fields come FROM the user?"
> Ask "Which fields are set automatically by the server? (timestamp)"
> Key: `read_only_fields = ['timestamp']` — user can't fake the timestamp.

```python
# Wiganz implements TransactionSerializer (serializers.py)
# Wiganz implements TransactionViewSet with list + create (views.py)
# Wiganz registers router.register(r'transactions', ...) (urls.py)
```

- [ ] **Step 11.3: Run all backend tests**

```bash
python manage.py test stocks -v 2
```

- [ ] **Step 11.4: Commit**

```bash
git add backend/stocks/
git commit -m "feat: Transaction serializer, GET/POST endpoints at /api/transactions/"
```

---

### Task 12: React Transaction Components

**Files:**
- Create: `frontend/src/hooks/useTransactions.js`
- Create: `frontend/src/components/TransactionForm.jsx`
- Create: `frontend/src/components/TransactionHistory.jsx`
- Modify: `frontend/src/App.jsx`

- [ ] **Step 12.1: Create transactions hook**

> 🎯 **Hadriel:** Ask "For the POST, what is `useMutation`? How is it different from `useQuery`?"
> Key insight: `useQuery` = read data. `useMutation` = change data. Different mental model.

```javascript
// frontend/src/hooks/useTransactions.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import client from '../api/client'

export function useTransactions() {
  return useQuery({
    queryKey: ['transactions'],
    queryFn: () => client.get('/api/transactions/').then(r => r.data),
  })
}

export function useCreateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data) => client.post('/api/transactions/', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })
}
```

- [ ] **Step 12.2: Wiganz builds TransactionForm**

> 🎯 **Hadriel:** Ask "What is a controlled component in React? Why do we use `useState` for form inputs?"
> This is where Wiganz learns the controlled input pattern for the first time.

```jsx
// frontend/src/components/TransactionForm.jsx — Wiganz implements
// State: ticker, type (buy/sell), price, quantity
// On submit: calls createTransaction.mutate({ ticker, type, price, quantity })
// On success: clear form
```

- [ ] **Step 12.3: Wiganz builds TransactionHistory**

```jsx
// frontend/src/components/TransactionHistory.jsx — Wiganz implements
// Props: none (fetches own data via useTransactions hook)
// Renders: table with timestamp, ticker, type, price, quantity
// Color: buy rows use accent-green, sell rows use accent-red
```

- [ ] **Step 12.4: Verify Slice 3 done gate**

✅ **Slice 3 done gate:**
- [ ] Transaction form submits and creates real record in DB
- [ ] Transaction history updates after form submission (no page reload)
- [ ] Portfolio P&L still works correctly (not broken by Slice 3 changes)
- [ ] All backend tests passing

- [ ] **Step 12.5: Commit**

```bash
git add frontend/src/
git commit -m "feat: Slice 3 complete — transaction form + history, useMutation pattern"
```

---

## SLICE 4: Signals Feature

```
╔══════════════════════════════════════════════════════════╗
║  🗄️  SDLC Phase 4 → 5 → 6: Signals Vertical Slice       ║
║  DB: No new table — signals computed from Alpha Vantage  ║
║  API: GET /api/stocks/<ticker>/signal/                   ║
║  UI: SignalBadge on Holdings + full SignalPanel          ║
║  Done when: Golden/Death Cross visible on each holding   ║
╚══════════════════════════════════════════════════════════╝
```

> **Hadriel teaching note — BEFORE this slice:**
> Ask "What is a Golden Cross? What is a Death Cross? Why do these signals matter to traders?"
> Ask "Should signal data be stored in the DB? Why not?"
> Key: signals are computed on demand from live MA data — storing them creates staleness problems.

---

### Task 13: MA Calculation Service + Signal Endpoint

**Files:**
- Modify: `backend/stocks/services.py`
- Modify: `backend/stocks/views.py`
- Modify: `backend/stocks/tests/test_services.py`

- [ ] **Step 13.1: Write failing tests for signal calculation**

```python
# Add to backend/stocks/tests/test_services.py

class SignalServiceTest(TestCase):
    def test_golden_cross_when_ma50_above_ma200(self):
        result = services.calculate_signal(ma50=182.30, ma200=178.20)
        self.assertEqual(result['signal'], 'Golden Cross')
        self.assertEqual(result['recommendation'], 'BUY')

    def test_death_cross_when_ma50_below_ma200(self):
        result = services.calculate_signal(ma50=175.00, ma200=178.20)
        self.assertEqual(result['signal'], 'Death Cross')
        self.assertEqual(result['recommendation'], 'SELL')

    def test_neutral_when_ma50_equals_ma200(self):
        result = services.calculate_signal(ma50=178.20, ma200=178.20)
        self.assertEqual(result['signal'], 'Neutral')
        self.assertEqual(result['recommendation'], 'HOLD')

    @patch('stocks.services.requests.get')
    def test_get_moving_averages_returns_ma50_and_ma200(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'Technical Analysis: SMA': {
                '2024-01-15': {'SMA': '182.30'},
                # ... more dates
            }
        }
        mock_get.return_value = mock_response
        result = services.get_moving_averages('AAPL')
        self.assertIn('ma50', result)
        self.assertIn('ma200', result)
```

- [ ] **Step 13.2: Wiganz implements signal service functions**

> 🎯 **Hadriel:** Ask "Where should the Golden/Death Cross decision logic live — in the view or in the service?"
> Key: business logic in services, HTTP handling in views. Always.

```python
# Add to backend/stocks/services.py — Wiganz implements:

def calculate_signal(ma50: float, ma200: float) -> dict:
    """Pure function — no DB, no API. Just math and logic."""
    # Wiganz implements with Hadriel guiding

def get_moving_averages(ticker: str) -> dict:
    """Fetch MA50 and MA200 from Alpha Vantage SMA endpoint."""
    # Wiganz implements — similar pattern to fetch_stock_price
```

- [ ] **Step 13.3: Add signal custom action to StockViewSet**

> 🎯 **Hadriel:** Ask "We already have a `fetch` action. How do we add a second custom action?"
> Ask "What is `detail=True` vs `detail=False` on an `@action`?"

```python
# Add to StockViewSet in backend/stocks/views.py

@action(detail=True, methods=['get'], url_path='signal')
def signal(self, request, ticker=None):
    """GET /api/stocks/<ticker>/signal/"""
    try:
        mas = services.get_moving_averages(ticker)
        result = services.calculate_signal(mas['ma50'], mas['ma200'])
        return Response({**result, 'ticker': ticker, **mas})
    except Stock.DoesNotExist:
        return Response({'error': f'Stock {ticker} not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
```

- [ ] **Step 13.4: Run all backend tests**

```bash
python manage.py test stocks -v 2
```

- [ ] **Step 13.5: Commit**

```bash
git add backend/stocks/
git commit -m "feat: MA signal service + /api/stocks/<ticker>/signal/ endpoint"
```

---

### Task 14: React Signal Components

**Files:**
- Modify: `frontend/src/hooks/useStocks.js`
- Create: `frontend/src/components/SignalPanel.jsx`
- Modify: `frontend/src/components/HoldingsLedger.jsx`
- Modify: `frontend/src/App.jsx`

- [ ] **Step 14.1: Add signal query to useStocks hook**

```javascript
// Add to frontend/src/hooks/useStocks.js

export function useSignal(ticker) {
  return useQuery({
    queryKey: ['signal', ticker],
    queryFn: () => client.get(`/api/stocks/${ticker}/signal/`).then(r => r.data),
    enabled: !!ticker,   // only fetch if ticker is provided
  })
}
```

- [ ] **Step 14.2: Wiganz builds SignalPanel**

> 🎯 **Hadriel:** Ask "What data does the SignalPanel display? Reference the SOVEREIGN screenshot from the spec."
> Fields: MA50 value, MA200 value, signal type, recommendation, today's gain, portfolio signal.

```jsx
// frontend/src/components/SignalPanel.jsx — Wiganz implements
// Props: ticker (string) — fetches its own signal data via useSignal hook
// Renders: SOVEREIGN-style right panel with MA values + signal recommendation
```

- [ ] **Step 14.3: Update HoldingsLedger to show signal badges**

> 🎯 **Hadriel:** Ask "Should HoldingsLedger fetch signals for each row? Or should signals come from the portfolio API?"
> Discussion: portfolio API doesn't include signals — we need to either add them to the API or fetch per-row.
> Guide Wiganz to decide: add signal field to PortfolioSerializer (cleaner — one API call vs N calls).

- [ ] **Step 14.4: Verify Slice 4 done gate**

✅ **Slice 4 done gate:**
- [ ] Signal badges visible on each holding row (Golden 🟢, Death 🔴, Neutral ⚪)
- [ ] SignalPanel shows MA50, MA200, recommendation for selected stock
- [ ] All 4 slices work together without breaking each other
- [ ] All backend tests passing

- [ ] **Step 14.5: Final integration commit**

```bash
git add frontend/src/ backend/stocks/
git commit -m "feat: Slice 4 complete — Golden/Death Cross signals, SignalPanel, signal badges"
```

---

## PHASE FINAL: Deploy

```
╔══════════════════════════════════════════════════════╗
║  🚀 SDLC — Phase 8: Deploy & Launch                 ║
║  Goal: Live app at Railway + Vercel URLs             ║
║  Output: deploy-guide.md + live URLs                 ║
╚══════════════════════════════════════════════════════╝
```

---

### Task 15: Railway Backend Deploy

**Files:**
- Create: `backend/Procfile`
- Create: `backend/railway.json`
- Create: `docs/deploy/deploy-guide.md`

- [ ] **Step 15.1: Add Railway config files**

```
# backend/Procfile
web: gunicorn quant_app.wsgi
```

```bash
pip install gunicorn
pip freeze > requirements.txt
```

- [ ] **Step 15.2: Update settings.py for production**

```python
# backend/quant_app/settings.py — production additions
import dj_database_url

if not DEBUG:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
    ALLOWED_HOSTS = ['*.railway.app']
    CORS_ALLOWED_ORIGINS = ['https://your-app.vercel.app']
```

- [ ] **Step 15.3: Deploy to Railway**

```bash
# 1. Push to GitHub
git add . && git commit -m "chore: add Railway production config"
git push origin main

# 2. Railway setup
# - Go to railway.app
# - New Project → Deploy from GitHub repo
# - Add PostgreSQL plugin
# - Set environment variables:
#   SECRET_KEY=<generate a strong key>
#   DEBUG=False
#   ALPHA_VANTAGE_KEY=<your key>

# 3. Run migrations on Railway
# In Railway console: python manage.py migrate
```

- [ ] **Step 15.4: Verify backend is live**

```bash
curl https://your-app.railway.app/api/stocks/
```

Expected: `[]` (empty list — no stocks yet on production DB)

---

### Task 16: Vercel Frontend Deploy

**Files:**
- Create: `frontend/vercel.json`

- [ ] **Step 16.1: Add Vercel config**

```json
// frontend/vercel.json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/" }]
}
```

- [ ] **Step 16.2: Deploy to Vercel**

```bash
# 1. Push to GitHub (already done)

# 2. Vercel setup
# - Go to vercel.com
# - New Project → Import from GitHub
# - Root Directory: frontend
# - Set environment variable:
#   VITE_API_URL=https://your-app.railway.app

# 3. Deploy
```

- [ ] **Step 16.3: Verify frontend is live**

Open `https://your-app.vercel.app` — should see the SOVEREIGN dashboard.

---

### Task 17: Production Smoke Test

- [ ] **Step 17.1: Run the production smoke test**

```
Open the Vercel URL in a browser.

Test 1: □ Dashboard loads — no white screen, no console errors
Test 2: □ Click "Refresh Price" on AAPL — price updates from Alpha Vantage
Test 3: □ Add a portfolio holding via Django admin → appears in Holdings table
Test 4: □ Record a buy transaction via the form — appears in Transaction History
Test 5: □ Signal panel shows Golden/Death Cross for a stock

All 5 pass → QuantApp is LIVE. 🎉
```

- [ ] **Step 17.2: Write the deploy guide**

```bash
# Create docs/deploy/deploy-guide.md
# Document: Railway steps, Vercel steps, all env variables, how to run migrations
```

- [ ] **Step 17.3: Final commit**

```bash
git add .
git commit -m "chore: production deploy complete — Railway + Vercel"
```

---

## Self-Review Against Spec

Checking every spec requirement:

| Spec Requirement | Covered In |
|---|---|
| Stock model (ticker, name, current_price, last_updated) | Task 3 |
| Portfolio model with @property pnl/pnl_percent | Task 7 |
| Transaction model (FK to Stock, buy/sell choices) | Task 10 |
| GET /api/stocks/ | Task 4 |
| POST /api/stocks/<ticker>/fetch/ | Task 5 |
| GET /api/stocks/<ticker>/signal/ | Task 13 |
| GET /api/portfolio/ with total_value, total_pnl | Task 8 |
| GET+POST /api/transactions/ | Task 11 |
| Golden/Death Cross logic (MA50 vs MA200) | Task 13 |
| React with TanStack Query | Tasks 6, 9, 12, 14 |
| TailwindCSS + CSS design tokens | Task 2 |
| SOVEREIGN + AMBER MACHINE + VIVID aesthetic | Tasks 9, 14 |
| Alpha Vantage 25-call constraint (Django caches) | Task 5 |
| Railway deploy | Task 15 |
| Vercel deploy | Task 16 |
| SDLC phase banners at each phase | All slice headers |
| Vertical slices — one feature done before next | Build order |

✅ All spec requirements covered. No gaps.

---

## How to Use This Plan

> **Every session starts here:**
> 1. Find the first unchecked `- [ ]` item
> 2. Hadriel calls the phase/slice banner
> 3. Hadriel asks the Socratic questions noted in `> 🎯 Hadriel:` callouts
> 4. Wiganz writes the code — Hadriel teaches the reasoning
> 5. Check off completed steps
> 6. Never start the next slice until the current slice's done gate passes

**Reference docs:**
- Spec: `docs/superpowers/specs/2026-04-15-quant-app-design.md`
- SDLC guide: `docs/learning-guides/sdlc-thinking-guide.md`
- Vertical slices guide: `docs/learning-guides/vertical-slices-guide.md`
