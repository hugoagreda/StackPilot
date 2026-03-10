# FastQR Backend (FastAPI)

MVP-oriented modular structure:
- `routes/`: HTTP layer
- `services/`: business rules
- `models/`: SQLAlchemy entities
- `schemas/`: Pydantic DTOs
- `utils/`: helpers (QR, time, security)

## Checkpoint tests

Run from workspace root:

```bash
.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.venv\\Scripts\\python.exe -m pytest -q apps/fastqr/backend/tests
```

Current checkpoint suite validates:
- app root and health endpoints
- public menu, votes, feedback, and ranking route behavior
- dashboard overview route behavior

## Supabase setup (database)

1. Copy `.env.example` (workspace root) to `apps/fastqr/backend/.env`.
2. Set `FASTQR_DATABASE_URL` with your Supabase project reference and password.
	- Format: `postgresql+psycopg://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres?sslmode=require`
3. In Supabase SQL Editor, run:
	- `apps/fastqr/database/migrations/001_init_fastqr.sql`
	- `apps/fastqr/database/seed.sql`

## Run API locally

From workspace root:

```bash
.venv\\Scripts\\python.exe -m uvicorn app.main:app --app-dir apps/fastqr/backend --reload --host 0.0.0.0 --port 8000
```

## Quick endpoint check

With seed data loaded, test menu endpoint:

```bash
curl http://localhost:8000/api/v1/public/demo-token-t1/menu
```
