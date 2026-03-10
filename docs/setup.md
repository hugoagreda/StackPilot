# StackPilot Setup Guide

## 1. Clone Repository
```bash
git clone <your-repo-url>
cd stackpilot
```

## 2. Configure Environment Variables
Copy and edit the environment templates:
- Root platform variables: `.env.example` -> `.env`
- Product variables: `apps/<product>/.env.example` -> `apps/<product>/.env`

## 3. Start Shared Infrastructure
```bash
docker compose up -d
```

## 4. Start Services
Run each service in development mode from its own directory as needed:
- `dashboard/frontend`
- `dashboard/backend`
- `apps/<product>/frontend`
- `apps/<product>/backend`

### Python App Virtual Environment Rule
Every micro-SaaS in `apps/` must use a virtual environment at the app root, not inside `backend/`.

Required structure:
```text
apps/
	<product>/
		venv/
		backend/
			requirements.txt
		frontend/
		database/
```

Install dependencies from `backend/requirements.txt` using that app-root environment.

Example (`apps/fastqr`):
```bash
cd apps/fastqr
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

## 5. Create New Product
Use `apps/template-app` as your baseline structure, then:
- Rename folder to your new product name
- Implement product-specific backend logic
- Connect product to core auth, billing, and analytics
- Add product visibility in dashboard modules

## Suggested Next Step
Automate product scaffolding in `scripts/` to make product creation one command.
