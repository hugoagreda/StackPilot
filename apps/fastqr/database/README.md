# FastQR Database

SQL del MVP FastQR.

## Que hace cada archivo

- `migrations/001_init_fastqr.sql`
	Crea tablas e indices iniciales del proyecto.
- `schema.sql`
	Snapshot de referencia del esquema completo.
- `seed.sql`
	Datos demo minimos (restaurante, categorias, platos, mesas y tokens QR).

## Inicializacion recomendada

1. Crear base de datos Postgres (local o Supabase).
2. Ejecutar migracion inicial.
3. Ejecutar seed demo.

En Supabase SQL Editor:

1. Ejecuta `migrations/001_init_fastqr.sql`.
2. Ejecuta `seed.sql`.

## Conexion desde backend

Define `FASTQR_DATABASE_URL` en el entorno del backend.

Formato:

```text
postgresql+psycopg://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres?sslmode=require
```

## Verificacion rapida

```sql
select count(*) from restaurants;
select count(*) from tables;
select count(*) from categories;
select count(*) from dishes;
```

## Tokens QR demo del seed

- `demo-token-t1`
- `demo-token-t2`

Ejemplo de prueba API:

`GET /api/v1/public/demo-token-t1/menu`

## Nota de login dashboard

`seed.sql` no crea usuarios en tabla `users`.
Para entrar al dashboard, crea un usuario valido antes de usar `/login`.
