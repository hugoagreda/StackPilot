# FastQR

FastQR es un micro-SaaS para restaurantes con dos experiencias:
- Cliente: escanea QR en mesa, ve menu, vota platos, deja feedback y consulta ranking diario.
- Restaurante: entra al dashboard, gestiona carta, mesas y descarga codigos QR.

## Estado actual (marzo 2026)

- Backend FastAPI: operativo.
- Frontend Next.js (App Router): operativo.
- Base de datos SQL (schema/migration/seed): disponible.
- Tests backend: pasando (`24 passed, 1 skipped`).

## Estructura de la app

- `backend/`
	API REST, autenticacion JWT y logica de negocio.
- `frontend/`
	Web de producto (cliente + dashboard).
- `database/`
	SQL de migraciones, esquema y seed.
- `config/`
	Guia y notas de configuracion por entorno.

## Levantamiento rapido de la web (local)

### 1) Instalar dependencias Python

Desde la raiz del workspace:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2) Levantar backend (terminal 1)

```powershell
cd apps/fastqr/backend

uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API disponible en:
- `http://localhost:8000`
- `http://localhost:8000/api/v1/health`

### 3) Levantar frontend (terminal 2)

En otra terminal:

```powershell
cd apps/fastqr/frontend
npm install
npm run dev
```

Web disponible en:
- `http://localhost:3000/dashboard`
- `http://localhost:3000/t/{token}`

## Flujo funcional esperado

1. Restaurante entra por `/dashboard`.
2. Ve resumen en `/dashboard`.
3. Gestiona categorias/platos en `/dashboard/dishes`.
4. Crea mesas y descarga QR en `/dashboard/tables`.
5. Cliente abre `/t/{token}` y usa menu + voto + feedback + ranking.

## Documentacion por modulo

- `backend/README.md`: API, endpoints y ejecucion backend.
- `frontend/README.md`: rutas web, estructura UI y arranque Next.js.
- `database/README.md`: migracion, seed y verificacion SQL.
- `config/README.md`: variables y convenciones de entorno.
