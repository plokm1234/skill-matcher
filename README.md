# Skill Matcher

Part of the Career GPS series. Paste a job description, pick a job title, and
see how your skills match — with a rule-based suggestion, not a guess.

Full design rationale, decision log, and architecture diagrams: see the
[Skill Matcher Blueprint](https://claude.ai/code/artifact/06d5895c-b15d-4bc9-b191-91fb1a7c9e76).

## What this demonstrates

- **Matching engine** — word-boundary regex matching from a skill
  dictionary outward into free text, so multi-word skills ("machine
  learning") match as whole phrases without tokenization.
- **Noise handling** — a marker-based heuristic (`extract_description_block`)
  that trims job-board page chrome from a raw copy-paste, validated against
  real CTgoodjobs and Indeed postings (see `backend/tests/test_matching.py`).
- **Relational schema** — PostgreSQL (Neon) with junction tables for the
  two many-to-many relationships (job ads ↔ skills, job titles ↔ skills).
- **Rule-based suggestions** — a deterministic decision tree (no AI) that
  distinguishes a same-track skill gap from a cross-track career change.
- **REST API** — FastAPI with auto-generated docs at `/docs`.

## Project structure

```
backend/
  app/
    matching.py      # skill dictionary → text matching + noise stripping
    suggestion.py     # match %, gap, and the rule-based suggestion
    database.py       # Postgres queries
    main.py            # FastAPI app, /extract and /titles endpoints
  db/
    schema.sql         # table definitions
    seed.sql            # starter skills + the 5 front-end job titles
  tests/
frontend/
  src/
    JobMatcher.jsx     # the whole UI: title row, manual/demo toggle, results
```

## Running locally

**Backend**

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Point at a Neon Postgres instance, then load the schema:
export DATABASE_URL="postgresql://..."
psql "$DATABASE_URL" -f db/schema.sql
psql "$DATABASE_URL" -f db/seed.sql

uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Tests**

```bash
cd backend
python -m pytest tests/ -v
```

## Known limitations

- The noise-stripping heuristic is marker-based, not a full HTML parser —
  it can miss the description block on job boards that don't use a
  "job description" style header.
- Demo hosting runs on free-tier infrastructure (Render + Neon); the first
  request after a period of inactivity may take up to a minute to respond.
