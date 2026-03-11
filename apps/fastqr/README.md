# FastQR

FastQR es una aplicacion para restaurantes basada en codigos QR, con dos experiencias principales:

- Cliente: escanea un QR en mesa, consulta el menu y vota platos.
- Restaurante: accede a un dashboard para gestionar carta, mesas y codigos QR.

## Arquitectura

- `backend/`
  API REST (FastAPI), autenticacion y logica de negocio.
- `frontend/`
  Aplicacion web (Next.js) para cliente y dashboard.
- `database/`
  Migraciones y SQL de soporte.
- `config/`
  Documentacion de configuracion por entorno.

## Tree del proyecto

```text
apps/fastqr/
|-- README.md
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- db.py
|   |   |-- main.py
|   |   |-- models/
|   |   |   |-- __init__.py
|   |   |   |-- category.py
|   |   |   |-- dish.py
|   |   |   |-- dish_score_override.py
|   |   |   |-- feedback.py
|   |   |   |-- game_reward_rule.py
|   |   |   |-- game_session.py
|   |   |   |-- restaurant.py
|   |   |   |-- restaurant_setting.py
|   |   |   |-- scoring_setting.py
|   |   |   |-- table.py
|   |   |   |-- table_access_session.py
|   |   |   |-- user.py
|   |   |   `-- vote.py
|   |   |-- routes/
|   |   |   |-- __init__.py
|   |   |   |-- auth.py
|   |   |   |-- dashboard.py
|   |   |   `-- public.py
|   |   |-- schemas/
|   |   |   |-- __init__.py
|   |   |   |-- analytics.py
|   |   |   |-- auth.py
|   |   |   |-- dashboard.py
|   |   |   |-- game.py
|   |   |   |-- public.py
|   |   |   `-- scoring.py
|   |   |-- services/
|   |   |   |-- __init__.py
|   |   |   |-- auth_service.py
|   |   |   |-- dashboard_service.py
|   |   |   |-- game_service.py
|   |   |   |-- public_service.py
|   |   |   `-- restaurant_service.py
|   |   `-- utils/
|   |       |-- auth.py
|   |       |-- common.py
|   |       `-- security.py
|   |-- tests/
|       |-- conftest.py
|       |-- test_dashboard_routes.py
|       |-- test_health.py
|       |-- test_public_integration_flow.py
|       |-- test_public_routes.py
|       `-- test_public_service.py
|   |-- fastqr_local.db
|   `-- README.md
|-- config/
|   `-- README.md
|-- database/
|   |-- migrations/
|   |   `-- 001_init_fastqr.sql
|   `-- README.md
|-- frontend/
|   |-- app/
|   |   |-- dashboard/
|   |   |   |-- dishes/
|   |   |   |-- tables/
|   |   |   |-- layout.tsx
|   |   |   `-- page.tsx
|   |   |-- login/
|   |   |   `-- page.tsx
|   |   |-- t/
|   |   |   `-- [token]/
|   |   |-- globals.css
|   |   |-- layout.tsx
|   |   `-- page.tsx
|   |-- components/
|   |   |-- DashboardCard.tsx
|   |   |-- DishCard.tsx
|   |   |-- MenuList.tsx
|   |   |-- QRTableCard.tsx
|   |   |-- TableRow.tsx
|   |   `-- VoteButton.tsx
|   |-- lib/
|   |   `-- api.ts
|   |-- next.config.mjs
|   |-- next-env.d.ts
|   |-- package.json
|   |-- package-lock.json
|   |-- postcss.config.mjs
|   |-- README.md
|   |-- tailwind.config.ts
|   `-- tsconfig.json
`-- README.md
```

## Requisitos

- Python 3.11+
- Node.js 20+
- npm 10+

## Arranque rapido (local)

### 1. Instalar dependencias Python

Desde la raiz del workspace:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Levantar backend

```powershell
cd apps/fastqr/backend
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend en `http://localhost:8000`.

### 3. Levantar frontend

En otra terminal:

```powershell
cd apps/fastqr/frontend
npm install
npm run dev
```

Frontend en `http://localhost:3000`.

## Rutas utiles

- Dashboard: `http://localhost:3000/dashboard`
- Vista cliente (ejemplo): `http://localhost:3000/t/demo-token-t1`
- Health backend: `http://localhost:8000/api/v1/health`

## Flujo funcional

1. El restaurante inicia sesion y entra al dashboard.
2. Gestiona platos y mesas.
3. Genera/descarga QR por mesa.
4. El cliente abre la ruta tokenizada `/t/{token}` y vota.

## Documentacion por modulo

- `apps/fastqr/backend/README.md`
- `apps/fastqr/frontend/README.md`
- `apps/fastqr/database/README.md`
- `apps/fastqr/config/README.md`
