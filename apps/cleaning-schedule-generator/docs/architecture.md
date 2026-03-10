# Architecture

Cleaning Schedule Generator MVP architecture.

## Components
- Frontend (Next.js): booking input and generated schedule UI.
- Backend API (FastAPI): validation, scheduling, and export.
- PostgreSQL: bookings, cleaners, and generated tasks.

## Domain Services
- booking_service: booking normalization and validation.
- cleaning_scheduler: slot generation and cleaner assignment.
- calendar_service: ICS export generation.

## Request Flow
1. User sends bookings, cleaner availability, and duration.
2. API validates and normalizes input payload.
3. Scheduler creates feasible cleaning tasks.
4. API returns schedule and optional ICS text.

## Deployment Notes
- Stateless API service.
- PostgreSQL as persistent store.
- Optional worker for recurring nightly recalculation.
