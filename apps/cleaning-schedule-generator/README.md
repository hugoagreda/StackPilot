# Cleaning Schedule Generator

Cleaning Schedule Generator is a micro-SaaS for automatically planning cleaning tasks between vacation rental reservations.
The product focus is reliability, operational speed, and fewer manual coordination errors.

## Role
This repository is implemented with a focus on:
- SaaS architecture for property operations
- Backend engineering for scheduling automation

## Project Context
Hosts and property managers need to coordinate cleaning windows between bookings.

The system generates cleanings based on:
- booking dates
- check-in/check-out times
- cleaning duration
- cleaner availability

## Target Users
- Vacation rental hosts
- Airbnb property managers
- Small property management teams

## Core Value
Automatically schedule cleanings between reservations and assign the right cleaner in feasible time windows.

## MVP Scope
MVP scope only, avoiding over-engineering and prioritizing development speed.

Includes:
- Booking input
- Cleaning duration configuration
- Automatic schedule generation
- Cleaner assignment
- Calendar export (.ics)

## Tech Stack
- Backend: FastAPI
- Frontend: React / Next.js
- Database: PostgreSQL

## Required Architecture
Modular backend architecture:

- backend/app/api: HTTP layer and endpoint versioning
- backend/app/services: business logic
- backend/app/models: SQLAlchemy entities
- backend/app/schemas: input/output DTOs
- backend/app/core: configuration and wiring

Key services:
- booking_service
- cleaning_scheduler
- calendar_service

### Micro structure
- backend: API FastAPI
- frontend: web client for bookings and generated schedules
- database: SQL schema and migrations
- config: environment configuration
- docs: architecture and decisions
- tests: MVP tests

Python environment note:
- Current virtual environment in backend/.venv
- Python dependencies in backend/requirements.txt

## Database Schema (MVP)
Main entities:
- properties: rental units managed by the host
- bookings: reservation windows per property
- cleaners: cleaner profile and status
- cleaner_availability: weekly availability windows for cleaners
- cleaning_tasks: generated cleaning assignments and status

Key relationships:
- property 1:N bookings
- cleaner 1:N cleaner_availability
- booking 1:1..N cleaning_tasks
- property 1:N cleaning_tasks
- cleaner 1:N cleaning_tasks

Recommended minimum fields:
- properties: id, host_id, name, timezone, created_at
- bookings: id, property_id, source, external_id, check_in, check_out, created_at
- cleaners: id, name, phone, email, is_active, created_at
- cleaner_availability: id, cleaner_id, day_of_week, start_time, end_time, created_at
- cleaning_tasks: id, booking_id, property_id, cleaner_id, start_at, end_at, status, exported_at, created_at

## Scheduling Algorithm (MVP)
Recommended flow:
1. Booking normalization
- Sort bookings by property and check_out.
- Build gaps between current booking check_out and next booking check_in.

2. Candidate slot generation
- For each booking, define an allowed window:
- start = booking.check_out
- end = next_booking.check_in (or fallback window if no next booking)

3. Cleaner assignment
- Iterate cleaners by current workload (fair distribution).
- For each cleaner availability window, attempt earliest feasible slot.
- Validate duration and avoid overlaps with already assigned tasks.

4. Conflict handling
- If no valid slot is found, mark as unscheduled with reason.
- Return scheduled and unscheduled lists in the response.

Heuristic objective:
- maximize scheduled tasks
- minimize idle time
- balance cleaner workload

## Backend API Design (MVP)
Suggested base path: /api/v1

Scheduling:
- POST /schedules/generate

Health endpoint:
- GET /health

Suggested next endpoints:
- POST /bookings/import
- GET /schedules?from={date}&to={date}
- PATCH /cleaning-tasks/{task_id}
- GET /calendar/export.ics?from={date}&to={date}

## MVP Architecture
Components:
- Next.js frontend for booking input and schedule visualization
- FastAPI backend for validation, scheduling, and exports
- PostgreSQL for bookings, availability, and generated tasks

Main flow:
1. User submits booking list and cleaner availability.
2. API validates payload and normalizes bookings.
3. cleaning_scheduler generates assignments and unresolved items.
4. calendar_service generates .ics output for external calendars.
5. Frontend displays schedule and unresolved conflicts.

## Quick start (Windows)
1. Create and activate backend venv:
- cd backend
- py -3 -m venv .venv
- .venv\Scripts\Activate.ps1

2. Install dependencies:
- pip install -r requirements.txt

3. Run API:
- uvicorn app.main:app --reload

API docs:
- http://127.0.0.1:8000/docs

## Clear Implementation Plan
1. Foundation setup
- Configure FastAPI, PostgreSQL, and environment variables
- Define base backend and frontend structure

2. Data layer
- Model MVP tables in SQLAlchemy
- Create initial migrations

3. Scheduling service
- Implement availability matching logic
- Implement conflict handling and unscheduled report
- Add basic fairness for cleaner assignment

4. API endpoints
- Create scheduling route and health route
- Validate payloads with Pydantic

5. Frontend experience
- Build booking input form
- Show generated schedule and unscheduled conflicts
- Add ICS export action

6. QA and hardening
- Test critical scheduling edge cases
- Add basic error handling and logging

7. Release MVP
- Deploy to staging environment
- Validate with 3-5 pilot hosts

## Constraints
- Focus on MVP only
- Avoid over-engineering
- Optimize development speed

## Goal
Have a clear implementation plan, a robust scheduling foundation, and a backend API ready to build Cleaning Schedule Generator iteratively and at scale.
