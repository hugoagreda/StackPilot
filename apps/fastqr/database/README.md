# FastQR Database (Supabase)

This folder contains SQL artifacts for the FastQR MVP database on Supabase Postgres.

## Files

- migrations/001_init_fastqr.sql: initial migration (DDL)
- schema.sql: consolidated schema snapshot
- seed.sql: minimal seed data for local/demo tests

## Supabase setup

1. Create a new Supabase project.
2. Open SQL Editor.
3. Run migrations/001_init_fastqr.sql.
4. Run seed.sql (optional but recommended for MVP tests).

## Backend connection

Set FASTQR_DATABASE_URL in backend environment:

postgresql+psycopg://postgres:[YOUR_DB_PASSWORD]@db.[YOUR_PROJECT_REF].supabase.co:5432/postgres?sslmode=require

Example .env entry for backend:

FASTQR_DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres?sslmode=require

## Quick verification queries

select count(*) from restaurants;
select count(*) from tables;
select count(*) from categories;
select count(*) from dishes;

## Seed test tokens

- demo-token-t1
- demo-token-t2

Use these tokens against public endpoints, for example:

GET /api/v1/public/demo-token-t1/menu
