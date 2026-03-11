# FastQR Frontend (Next.js)

Frontend MVP de FastQR para dos perfiles:
- Cliente que escanea QR y ve el menu.
- Restaurante que gestiona carta y mesas desde dashboard.

## Stack

- Next.js (App Router)
- React + TypeScript
- TailwindCSS

## Estructura

- `app/login/page.tsx`
	Redireccion temporal a dashboard (login desactivado).
- `app/dashboard/page.tsx`
	Resumen simple: votos, valoraciones, nota media, sesiones.
- `app/dashboard/dishes/page.tsx`
	Gestion de categorias y platos (crear, editar, disponibilidad).
- `app/dashboard/tables/page.tsx`
	Gestion de mesas y descarga de QR.
- `app/t/[token]/page.tsx`
	Vista cliente para menu, voto, feedback y ranking diario.
- `components/`
	Componentes UI reutilizables (`DishCard`, `MenuList`, `VoteButton`, etc).
- `lib/api.ts`
	Cliente de API para hablar con FastAPI (`/api/v1/...`).

## Levantamiento local de la web

Requisitos:
- Node.js 18+
- Backend FastQR levantado en `http://localhost:8000`

1. Instalar dependencias del frontend

```powershell
cd apps/fastqr/frontend
npm install
```

2. Levantar web en modo desarrollo

```powershell
npm run dev
```

3. Abrir en navegador

- `http://localhost:3000/dashboard` para dashboard.
- `http://localhost:3000/t/{token}` para vista cliente.

## Build de produccion

```powershell
cd apps/fastqr/frontend
npm run build
npm run start
```

## Nota temporal

El login esta desactivado temporalmente en frontend.
