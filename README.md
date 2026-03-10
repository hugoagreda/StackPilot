# StackPilot

StackPilot is a micro-SaaS platform architecture designed to manage multiple products from a single control plane while keeping each product operationally independent.

## Architecture Principles
- Central control dashboard
- Independent micro-products
- Shared infrastructure services

Each product should have:
- Its own frontend/backend stack
- Its own database
- Independent business logic
- Its own Python virtual environment at `apps/<product>/venv`

Python dependency rule for apps:
- Create the virtual environment at the app root (`apps/<product>/venv`)
- Keep dependency files in backend (`apps/<product>/backend/requirements.txt`)
- Install backend dependencies using the app-root environment

Shared services include:
- Authentication
- Billing
- Analytics
- Notifications
- Deployment infrastructure

The goal of this architecture is to reduce friction and time-to-market when launching new products.

## Monorepo Structure
```text
stackpilot/
	.env.example
	.venv/
	apps/
		cleaning-schedule-generator/
			backend/
			config/
			database/
			docs/
			frontend/
			tests/
		fastqr/
			.env.example
			frontend/
			backend/
			config/
			database/
			tests/
		meetingtasks/
			backend/
			config/
			docs/
			frontend/
			infra/
			tests/
		rental-price-estimator/
			backend/
			config/
			database/
			docs/
			frontend/
		template-app/
			.env.example
			frontend/
			backend/
			config/
			database/
			tests/

	core/
		README.md
		auth/
		billing/
		analytics/
		notifications/
		shared-utils/

	dashboard/
		README.md
		frontend/
		backend/

	packages/
		README.md
		ui-components/
		api-client/
		shared-types/

	infra/
		docker/
		deployment/

	scripts/
		README.md
	docs/
		architecture.md
		setup.md
	README.md
	docker-compose.yml
	.gitignore
	.git/
```

## Quick Start
1. Copy available environment templates:
	 - `.env.example` -> `.env`
	 - `apps/fastqr/.env.example` -> `apps/fastqr/.env`
	 - `apps/template-app/.env.example` -> `apps/template-app/.env`
2. Start shared infrastructure:
	 - `docker compose up -d`
3. For each Python-based app, create and use its app-root virtual environment (`apps/<product>/venv`).
4. Build product and dashboard services from their own folders.

### Python App Environment Convention
For each app under `apps/`, use one virtual environment at app root:

```text
apps/
	<product>/
		venv/
		backend/
			requirements.txt
		frontend/
		database/
```

Example (from `apps/fastqr`):

```bash
cd apps/fastqr
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1

pip install -r backend/requirements.txt
```

## Documentation
- Architecture details: `docs/architecture.md`
- Setup walkthrough: `docs/setup.md`

## Product Launch Workflow
1. Copy `apps/template-app` into a new app folder.
2. Implement product-specific backend/domain logic.
3. Connect shared services from `core/`.
4. Register product in the dashboard.
5. Configure deployment under `infra/deployment`.