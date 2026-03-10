# FastQR

FastQR is a micro-SaaS for restaurant table interaction through QR codes.
The product focus is customer engagement and actionable analytics on dishes, not just a digital menu.

## Current Status (March 2026)

Implementation status by layer:
- Backend API: in progress (core public flow implemented)
- Database: in progress (schema + migration + seed available)
- Frontend: not started (README only)
- End-to-end flow: partially available (API side)

What is working today:
- Health endpoint
- Public menu by QR token
- Public vote endpoint
- Public feedback endpoint
- Public daily ranking endpoint
- Dashboard overview endpoint (currently without authentication)
- Backend test checkpoint suite

What is missing for MVP completion:
- Frontend app for customer and manager flows
- Dashboard authentication (login/token protection)
- Table QR generation endpoint
- Dashboard CRUD for dishes and table management
- Stronger integration tests with a real test database

## Role
This repository is implemented with a focus on:
- SaaS product architecture
- Backend engineering for restaurant tech

## Project Context
Each restaurant table has a QR code that opens a digital interface for customers.
From that interface, the customer can:
- View the menu
- Vote for dishes
- Leave feedback
- Participate in daily rankings

## Target Users
- Restaurants
- Bars
- Tapas restaurants
- Small hospitality businesses

## Core Value
Improve customer interaction and capture insights about dish preferences and behavior by table, time slot, and day.

## MVP Scope
MVP scope only, avoiding over-engineering and prioritizing development speed.

Includes:
- Restaurant dashboard
- QR generator per table
- Digital menu viewer
- Dish voting system
- Daily dish ranking
- Basic analytics

## Tech Stack
- Backend: FastAPI
- Frontend: React / Next.js
- Database: PostgreSQL
- Infra: Docker

## Required Architecture
Modular backend architecture:

- backend/routes: HTTP layer and endpoint versioning
- backend/services: business logic
- backend/models: SQLAlchemy entities
- backend/schemas: input/output DTOs
- backend/utils: helpers and shared utilities

### Micro structure
- backend: API FastAPI
- frontend: web client for menu and dashboard
- database: SQL scripts and initial seed
- tests: MVP tests

Python environment note:
- Current virtual environment in workspace root /.venv
- Python dependencies in /requirements.txt (workspace root)

## Database Schema (MVP)
Main entities:
- restaurants: restaurant data
- tables: tables associated with a restaurant
- categories: menu categories
- dishes: dishes by category
- votes: dish votes by table
- feedback: comments, rating, and table context
- users: restaurant admin user

Key relationships:
- restaurant 1:N tables
- restaurant 1:N categories
- category 1:N dishes
- table 1:N votes
- dish 1:N votes
- table 1:N feedback
- dish 1:N feedback (optional in MVP)

Recommended minimum fields:
- restaurants: id, name, slug, created_at
- tables: id, restaurant_id, number, qr_token, is_active
- dishes: id, restaurant_id, category_id, name, description, price, is_available
- votes: id, restaurant_id, table_id, dish_id, vote_value, created_at
- feedback: id, restaurant_id, table_id, dish_id, comment, rating, created_at

## Backend API Design (MVP)
Suggested base path: /api/v1

Implemented endpoints:
- GET /health
- GET /public/{qr_token}/menu
- POST /public/{qr_token}/votes
- POST /public/{qr_token}/feedback
- GET /public/{qr_token}/ranking/today
- GET /dashboard/overview?restaurant_slug={slug}

Planned dashboard/auth endpoints (next iterations):
- POST /dashboard/login
- GET /dashboard/{restaurant_slug}/dishes/ranking/today
- GET /dashboard/{restaurant_slug}/feedback/recent
- POST /dashboard/{restaurant_slug}/tables/{table_id}/qr
- CRUD /dashboard/{restaurant_slug}/dishes

## Minimal Frontend Structure
frontend/
- app/
- app/menu/[slug]/page.tsx
- app/table/[token]/page.tsx
- app/dashboard/page.tsx
- components/
- lib/api-client.ts
- styles/

Current frontend note:
- This structure is the target architecture.
- The frontend implementation has not been scaffolded yet.

MVP frontend goal:
- Fast flow for customers scanning a QR
- Simple dashboard for owner/manager
- Direct integration with FastAPI endpoints

## Clear Implementation Plan
1. Foundation setup
- Configure FastAPI, PostgreSQL, and local Docker Compose
- Define environment variables and DB connection

2. Data layer
- Model MVP tables in SQLAlchemy
- Create initial migrations
- Load minimal seed data (categories, dishes, tables)

3. Public experience
- Menu endpoint by slug
- Dish vote endpoint
- Feedback endpoint
- Daily ranking endpoint

4. Dashboard experience
- Basic login for restaurant users
- Activity summary (votes, feedback, top dishes)
- Minimum table and dish management

5. Analytics MVP
- Daily aggregates by dish
- Vote count by time slot
- Average rating by dish

6. QA and hardening
- Test critical routes
- Validate payloads with Pydantic
- Add basic error handling and logging

7. Release MVP
- Deploy to staging environment
- Functional verification with 1 pilot restaurant

## Immediate Next Steps (Execution Order)
1. Harden backend dashboard layer
- Add minimal authentication guard for dashboard routes
- Add detail endpoints for ranking and recent feedback

2. Start frontend scaffold
- Create React or Next.js project in `frontend/`
- Add API client and env wiring (`NEXT_PUBLIC_API_URL`)

3. Build first end-to-end vertical slice
- Customer: token -> menu -> vote -> feedback
- Manager: dashboard overview + daily ranking + recent feedback

4. Stabilize with tests
- Expand backend tests for auth and conflict-safe voting
- Add one integration test path with seeded database

## Constraints
- Focus on MVP only
- Avoid over-engineering
- Optimize development speed

## Goal
Have a clear implementation plan and a backend API design ready to build FastQR iteratively and at scale.
