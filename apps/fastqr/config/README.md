# FastQR Config

Esta carpeta documenta convenciones de configuracion por entorno (`dev`, `staging`, `prod`).

## Variables importantes

Backend:
- `FASTQR_DATABASE_URL`: conexion SQLAlchemy a Postgres.
- `FASTQR_JWT_SECRET`: secreto para firmar tokens JWT.
- `FASTQR_JWT_ALGORITHM`: algoritmo JWT (default `HS256`).
- `FASTQR_JWT_EXPIRE_MINUTES`: expiracion del token en minutos.

Frontend:
- En local se usa proxy/rewrite en Next.js hacia `http://localhost:8000/api/v1`.

## Recomendaciones

- Nunca commitear secretos reales.
- Usar secretos distintos por entorno.
- Mantener variables de backend fuera del frontend.

## Arranque local (resumen)

1. Configura variables backend.
2. Levanta API FastAPI en puerto `8000`.
3. Levanta frontend Next.js en puerto `3000`.
