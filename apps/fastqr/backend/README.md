# FastQR Backend (FastAPI)

API del MVP FastQR.

## Que hace cada carpeta

- `app/routes/`
	Define endpoints HTTP (`/api/v1/...`) y validaciones de entrada/salida.
- `app/services/`
	Contiene la logica de negocio (votos, ranking, platos, mesas, auth).
- `app/models/`
	Modelos SQLAlchemy conectados a tablas de base de datos.
- `app/schemas/`
	DTOs Pydantic para requests/responses.
- `app/utils/`
	Helpers comunes (JWT, hash de password, auth helpers).

## Endpoints principales

Public (cliente):
- `GET /api/v1/public/{qr_token}/menu`
- `POST /api/v1/public/{qr_token}/votes`
- `POST /api/v1/public/{qr_token}/feedback`
- `GET /api/v1/public/{qr_token}/ranking/today`

Auth:
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

Dashboard (requiere JWT):
- `GET /api/v1/dashboard/restaurants/{restaurant_id}/overview`
- `GET /api/v1/dashboard/restaurants/{restaurant_id}/categories`
- `POST /api/v1/dashboard/restaurants/{restaurant_id}/categories`
- `GET /api/v1/dashboard/restaurants/{restaurant_id}/dishes`
- `POST /api/v1/dashboard/restaurants/{restaurant_id}/dishes`
- `PATCH /api/v1/dashboard/restaurants/{restaurant_id}/dishes/{dish_id}`
- `GET /api/v1/dashboard/restaurants/{restaurant_id}/tables`
- `POST /api/v1/dashboard/restaurants/{restaurant_id}/tables`

## Levantar backend local

Desde la raiz del workspace:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps/fastqr/backend --reload --host 0.0.0.0 --port 8000
```

Health check:

```powershell
curl http://localhost:8000/api/v1/health
```

## Tests backend

```powershell
.venv\Scripts\python.exe -m pytest -q apps/fastqr/backend/tests
```

## Configuracion de base de datos

Variables esperadas en entorno del backend:
- `FASTQR_DATABASE_URL`
- `FASTQR_JWT_SECRET`
- `FASTQR_JWT_ALGORITHM` (opcional, default `HS256`)
- `FASTQR_JWT_EXPIRE_MINUTES` (opcional)

Para detalles de SQL, revisa `../database/README.md`.
