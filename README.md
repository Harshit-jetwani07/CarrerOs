# CareerOS

AI-powered career intelligence platform — analyzes a student's resume and
skills, matches them against target roles with an explainable scoring
model, finds skill gaps, and generates a personalized week-by-week
roadmap.

> Analyze. Discover. Upskill. Get Career-Ready.

## What's implemented (MVP)

- Auth (register/login, JWT)
- Resume upload (validated PDF/DOCX) → text extraction → AI-structured analysis
  (scores, strengths/weaknesses, ATS check, bullet rewrites)
- Career role matching — a transparent weighted score (skill match,
  project evidence, experience, education, interest), not a black box
- Skill gap analysis, prioritized HIGH/MEDIUM/LOW per target role
- Personalized roadmap generation (week-by-week, with why/practice/project
  per topic)
- Job description analyzer — paste a JD, get evidence-backed matched, partial,
  and missing requirements
- Resume Builder — premium SyncLyft-style template with PDF and DOCX export
- Settings — connect a user-owned OpenAI, Gemini, or Groq key (encrypted at rest)

The AI layer works in **offline demo mode** with sensible fallback data if
you don't add an OpenAI key yet — so you can run and click through the
whole app before wiring up billing.

## Tech stack

| Layer      | Choice                                              |
|------------|------------------------------------------------------|
| Frontend   | Next.js 14 (App Router) + TypeScript + Tailwind CSS  |
| Backend    | FastAPI + SQLAlchemy + Alembic                       |
| Database   | PostgreSQL                                           |
| Cache      | Redis (optional, for later use)                      |
| AI         | OpenAI, Gemini, Groq, with offline fallback           |
| Auth       | Self-contained JWT (swap for Clerk/Auth.js anytime)  |
| Documents  | PyMuPDF (PDF), python-docx (DOCX)                    |
| Charts     | Recharts                                             |

## Prerequisites

Install these once, in this order:

1. **Python 3.11+** — https://www.python.org/downloads/
2. **Node.js 20+** (includes npm) — https://nodejs.org/
3. **PostgreSQL 16** — either install locally
   (https://www.postgresql.org/download/windows/) **or** just use Docker
   (see the Docker section below, easiest option).
4. **Git** (optional but recommended) — https://git-scm.com/

## Option A — Run with Docker (easiest for Postgres)

This spins up Postgres + Redis in containers; you still run the backend
and frontend directly so you get instant reload during development.

```bash
# 1. From the CareerOS folder, create the backend environment file
cd backend
copy .env.example .env        # Windows
# cp .env.example .env        # Mac/Linux

# 2. Start Postgres + Redis
cd ..
docker compose up -d postgres redis

# 3. Continue with the "Backend setup" and "Frontend setup" steps below
```

## Option B — No Docker

Install PostgreSQL locally, then create the database and user:

```sql
CREATE DATABASE careeros;
CREATE USER careeros WITH PASSWORD 'careeros';
GRANT ALL PRIVILEGES ON DATABASE careeros TO careeros;
```

Then set `DATABASE_URL` in `backend/.env` to match.

## Backend setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in your values (DATABASE_URL, JWT_SECRET,
# FERNET_SECRET_KEY). JWT_SECRET is required in production.
copy .env.example .env          # Windows
# cp .env.example .env          # Mac/Linux

# Apply the schema migrations
alembic upgrade head

# Seed the role/skill dataset (Backend Developer, Frontend Developer, etc.)
python seed.py

# Run the API
uvicorn app.main:app --reload
```

The API is now live at **http://localhost:8000** — check
**http://localhost:8000/docs** for the interactive Swagger UI (auto-generated,
great for testing endpoints without the frontend).

> In development, the API can create missing tables to keep first-run setup
> simple. Use `alembic upgrade head` as the normal and production-safe schema
> setup path.

## Frontend setup

Open a **second terminal** (keep the backend running in the first):

```bash
cd frontend

npm install

copy .env.local.example .env.local     # Windows
# cp .env.local.example .env.local     # Mac/Linux

npm run dev
```

Open **http://localhost:3000** — sign up, and you're in.

## Getting a real AI response (optional but recommended)

Without a connected key, analysis and roadmap generation use clearly-labeled
offline fallback logic so the app still works end-to-end. To get real AI output:

1. Create an account and open **Dashboard → Settings**.
2. Connect your own OpenAI, Gemini, or Groq API key.
3. The key is encrypted server-side and never returned to the browser.

For server-managed development keys only, `OPENAI_API_KEY` can still be set in
`backend/.env`. Do not commit `.env` files. Set a long, random `JWT_SECRET`
and `FERNET_SECRET_KEY` before deploying.

## Project structure

```
CareerOS/
├── backend/
│   ├── app/
│   │   ├── models/       # SQLAlchemy tables
│   │   ├── schemas/      # Pydantic request/response shapes
│   │   ├── routers/      # API endpoints, grouped by feature
│   │   ├── services/     # Business logic (matching, skill-gap, AI, roadmap)
│   │   ├── data/         # Seed data (roles + required skills)
│   │   ├── main.py       # FastAPI app entrypoint
│   │   └── config.py     # Settings from environment variables
│   ├── alembic/          # DB migrations
│   └── seed.py           # Populates the role/skill dataset
└── frontend/
    ├── app/               # Next.js pages (App Router)
    │   └── dashboard/     # Resume, Career Match, Skill Gap, Roadmap, Jobs
    ├── components/        # Sidebar, gauge, cards, shared UI primitives
    └── lib/                # API client, types, auth helper
```

## What to build next (in priority order)

1. **Password reset and email verification** — require a transactional email
   service before enabling account recovery in production.
2. **Redis-backed auth throttling** — the current local limiter protects a
   single API process; use Redis when deploying multiple API instances.
3. **pgvector semantic matching** — swap the keyword-based JD skill match
   for embedding similarity, for messier real-world job postings.
4. **Tests** — expand `pytest` coverage for backend services, especially
   `matching_service` and `skill_gap_service` since their scoring logic
   is the product's core differentiator.
5. **Deploy** — Vercel (frontend), Render/Railway (backend), Supabase or
   Neon (Postgres). All three have generous free tiers for a student
   project.

## Troubleshooting

- **`psycopg2` fails to install on Windows** → install
  "Microsoft C++ Build Tools" or use `pip install psycopg2-binary`
  (already in requirements.txt, this should just work).
- **CORS errors in the browser console** → make sure
  `FRONTEND_ORIGIN` in `backend/.env` matches the URL you're opening
  the frontend on exactly (including port).
- **"No roadmap yet" even after generating** → generate happens per role;
  make sure you're viewing the same role tab you generated for.
