# OrientIA

AI platform helping Moroccan students find matching French/international university
programs, prepare application documents, and track deadlines — powered by a real
tool-calling agent, not a single-prompt chatbot.

## What's actually implemented

| Feature | Where | Status |
|---|---|---|
| RAG program matching (pgvector + grounded LLM ranking) | `backend/app/services/rag.py` | Functional, needs Supabase + OpenAI key |
| Tool-calling agent (deadlines, eligibility, letter drafts, missing docs) | `backend/app/services/agent.py` | Functional, needs Groq/OpenAI key |
| Document AI (PDF transcript → grades → weak-spot flags) | `backend/app/services/document_ai.py` | Functional for text-based PDFs (no OCR yet) |
| Kanban application tracker | `frontend/app/dashboard`, `backend/app/routers/applications.py` | Functional |
| Auth | Supabase Auth (frontend) + `profiles` sync (backend) | Functional |
| Scraper (Campus France / Parcoursup ingestion) | `backend/app/scraper/university_pages.py` | **Sketch only** — see note below |

### Why the scraper is a sketch, not a crawler
Campus France and Parcoursup don't expose a stable public API, and their page
structures aren't uniform across universities. A generic crawler would be brittle
and could run into each site's terms of use. The realistic path — and the one
worth describing in an interview — is: hand-pick target program pages, extract
with `fetch_page_text()`, and feed them through `ingest_program()`. For the demo
and for development, `backend/app/data/seed_programs.json` + `scripts/seed_db.py`
populate the catalog with six realistic L3 Informatique programs (Sorbonne,
Grenoble Alpes, INSA Lyon, Bordeaux, Côte d'Azur, Paris-Saclay) so the RAG
pipeline, agent, and matching UI all work end-to-end without needing live scraping.

## Architecture

```
frontend/  Next.js 14 (App Router) + TypeScript + Tailwind
           — landing, program matching, transcript upload, agent chat, kanban dashboard
backend/   FastAPI
           — RAG matching, agent tool-calling, document AI, applications CRUD
           — Supabase (Postgres + pgvector + Auth) as the only datastore
```

The agent and RAG both talk to an OpenAI-compatible chat-completions API —
configured via `LLM_PROVIDER=groq` (fast, generous free tier) or `openai`.
Embeddings always go through OpenAI (Groq doesn't serve embedding models),
so an `OPENAI_API_KEY` is required either way, even if you run everything
else on Groq.

## Setup

### 1. Supabase project
1. Create a project at [supabase.com](https://supabase.com).
2. Open the SQL editor and run `backend/app/db/schema.sql` — this enables
   pgvector, creates all tables, the similarity-search function, and RLS
   policies.
3. Copy your project URL, anon key, and service-role key from
   Settings → API.

### 2. Backend
```bash
cd backend
cp .env.example .env        # fill in Supabase + Groq/OpenAI keys
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.seed_db    # populates the sample program catalog + embeddings
uvicorn app.main:app --reload
```
API docs at `http://localhost:8000/docs`.

### 3. Frontend
```bash
cd frontend
cp .env.local.example .env.local   # fill in Supabase URL/anon key + API URL
npm install
npm run dev
```
App at `http://localhost:3000`.

### 4. Docker (both services)
```bash
docker compose up --build
```

## Deployment (same zero-cost pattern as your hotel project)
- **Frontend → Vercel**: import the repo, set the three `NEXT_PUBLIC_*` env vars,
  root directory `frontend/`.
- **Backend → Railway**: new service from repo, root directory `backend/`,
  set env vars from `.env.example`, Railway auto-detects the `Dockerfile`.
- **Database → Supabase** (already hosted, no separate deploy step).

## Known gaps / next steps
- **Auth wiring in the UI**: `login/page.tsx` calls real Supabase Auth, but
  `dashboard`, `agent`, and `transcript` pages currently use a
  `DEMO_USER_ID` placeholder instead of reading the live session. Swap in
  `supabase.auth.getSession()` (e.g. via a small client-side auth context)
  before this is usable by more than one person.
- **OCR for scanned transcripts**: `document_ai.py` raises a clear error on
  image-only PDFs rather than silently failing. Add `pytesseract` +
  `pdf2image` if you need to support scanned transcripts.
- **Stripe premium tier**: not built yet — bolt onto the `applications`
  table with a `plan` column on `profiles` when you're ready to gate
  features (e.g. limit free users to 3 tracked applications).
- **Real scraper**: see note above.
