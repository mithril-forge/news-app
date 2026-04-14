# Tvůj Novinář — AI-Powered Czech News Platform

A full-stack news aggregation platform that uses AI to curate personalized news collections from Czech sources. Users can generate a custom "news pick" — a ranked selection of articles chosen by an AI based on their own prompt — without needing an account.

---

## What it does

The platform solves a real problem: reading the news is time-consuming and most aggregators show everything without filtering for relevance. This app lets you describe what you care about in plain language, and the AI does the filtering for you.

**Core user flows:**

- Browse the latest Czech news, sorted by recency or a relevance score that accounts for time decay and article popularity
- Search full-text across all articles
- Generate a personalized "news pick" — paste a prompt describing your interests, get back a curated shortlist with AI-written summaries
- Create an account to save your prompt and get a fresh pick generated daily
- Share any pick via a unique URL

**Business value highlights:**

- Zero friction for anonymous users — no account required to generate a pick
- Personalization scales cheaply: a single background job generates picks for all registered users once a day
- News sources and processing are fully automated; no editorial team needed
- Relevance scoring surfaces high-quality content without manual curation

---

## Technical overview

### Architecture

Monorepo with a clear frontend/backend split, deployed as Docker containers on a VPS via [Dokploy](https://dokploy.com).

```
news-app/
├── frontend/     # Next.js 15 app
├── backend/      # FastAPI Python app
│   ├── core/     # Domain models, services, repository layer
│   └── features/ # AI processing pipeline (scraping → parsing → enrichment)
└── envs/         # Environment config templates
```

### Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS 4 |
| Backend | FastAPI, Python 3.13, SQLModel (async) |
| Database | PostgreSQL 17 with a materialized view for relevance scoring |
| Cache / Queue | Redis 8 (broker for background tasks + caching) |
| Background jobs | Dramatiq + Periodiq (cron-style scheduling) |
| AI | Google Gemini via Instructor (structured output) |
| Email | Brevo transactional API |
| Deployment | Docker Compose, GitHub Actions CI, Dokploy |

### AI pipeline

Raw articles go through a multi-step enrichment pipeline running as background jobs:

1. **Scrape** — fetch new articles from Czech news sources (3× daily)
2. **Connect** — link new input articles to existing parsed articles via AI analysis
3. **Enrich** — generate structured article data (title, summary, tags, importance score 1–10, topic)
4. **Pick generation** — daily job produces a ranked news pick for every registered account using their stored prompt

The AI layer uses an abstract interface (`AbstractAIModel`) so the provider (currently Gemini) can be swapped for OpenAI without touching business logic.

### Relevance scoring

A PostgreSQL materialized view (`ParsedNewsRelevancy`) computes a composite score per article combining:
- Time decay (newer articles score higher)
- View count (popular articles get a boost)

The view refreshes every 5 minutes via a scheduled Dramatiq task.

### Notable design decisions

- **Async-first backend** — full `async/await` across the FastAPI app and SQLModel queries for high concurrency without threading complexity
- **Repository pattern** — typed generic repositories isolate data access from business logic, making services testable and the ORM swappable
- **Structured logging** — Structlog outputs JSON logs at every service layer, making production debugging straightforward
- **Anonymous pick claiming** — a user can generate a pick anonymously, then create an account and claim that pick retroactively
- **Secure account deletion** — token-based flow with 24-hour expiry, hash storage (token itself never stored), and IP/user-agent logging

---

## Running locally

Requires Docker and Docker Compose.

```bash
cp envs/.env.example envs/.env   # fill in API keys
docker compose up
```

The frontend is available at `http://localhost:3000`, the backend API at `http://localhost:8000`.

**Useful Make targets:**

```bash
make up           # start all services
make down         # stop services
make logs         # tail all logs
make logs backend # tail a single service
make ruff         # lint backend
make mypy         # type-check backend
```

### Environment variables

| Variable | Purpose |
|---|---|
| `GOOGLE_API_KEY` | Gemini API access |
| `BREVO_API_KEY` | Transactional email |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `NEXT_PUBLIC_API_URL` | Backend URL used by the frontend |

---

## CI

GitHub Actions runs on every push to `main`/`develop` and on all pull requests:

- Ruff lint + format check
- MyPy strict type checking

Config: `.github/workflows/backend.yml`
