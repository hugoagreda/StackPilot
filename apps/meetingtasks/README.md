# MeetingTasks

MeetingTasks is a micro-SaaS for turning meeting content into actionable tasks.
The product focus is execution, clear ownership, and deadline tracking.

## Role
This repository is implemented with a focus on:
- SaaS product architecture
- Backend engineering for AI productivity tools

## Project Context
MeetingTasks transforms unstructured meeting content into structured outputs.

Users can provide:
- Meeting transcript
- Meeting notes
- Meeting recording

The system extracts:
- Key decisions
- Tasks
- Responsible person
- Deadlines

## Target Users
- Startups
- Agencies
- Remote teams
- Founders

## Core Value
Transform meeting discussions into actionable plans with clear tasks, due dates, and ownership.

## MVP Scope
MVP scope only, avoiding over-engineering and prioritizing development speed.

Includes:
- Transcript input
- AI task extraction
- Meeting summary
- Task list with owner and deadline
- Task export in JSON and Markdown

## Future Scope (Post-MVP)
- Zoom integration
- Microsoft Teams integration
- Notion export
- Slack export

## Tech Stack
- Backend: FastAPI
- Frontend: Next.js
- AI: LLM API
- Database: PostgreSQL

## Required Architecture
Modular backend architecture:

- backend/app/api: HTTP layer and endpoint versioning
- backend/app/services: business logic
- backend/app/models: SQLAlchemy entities
- backend/app/schemas: input/output DTOs
- backend/app/core: configuration and wiring

Key services:
- meeting_service
- task_extraction_service
- summary_service

### Micro structure
- backend: API FastAPI
- frontend: web client for input and visualization
- docs: functional and technical documentation
- infra: local environment resources
- tests: MVP tests

Python environment note:
- Current virtual environment in backend/.venv
- Python dependencies in backend/requirements.txt

## Database Schema (MVP)
Main entities:
- meetings: meeting metadata and raw inputs
- meeting_summaries: AI-generated summary
- meeting_decisions: extracted key decisions
- tasks: actionable tasks with owner and due date
- ai_runs: traceability of AI runs

Key relationships:
- meeting 1:N tasks
- meeting 1:N meeting_decisions
- meeting 1:N meeting_summaries
- meeting 1:N ai_runs

Recommended minimum fields:
- meetings: id, title, source_type, raw_transcript, raw_notes, recording_url, processing_status, created_at
- meeting_summaries: id, meeting_id, summary_text, created_at
- meeting_decisions: id, meeting_id, decision_text, confidence, created_at
- tasks: id, meeting_id, title, description, owner_name, due_date, priority, status, created_at
- ai_runs: id, meeting_id, run_type, model_name, status, latency_ms, created_at

## Backend API Design (MVP)
Suggested base path: /api/v1

Meetings:
- POST /meetings
- GET /meetings/{meeting_id}
- POST /meetings/{meeting_id}/process
- GET /meetings/{meeting_id}/results

Tasks:
- GET /meetings/{meeting_id}/tasks
- PATCH /tasks/{task_id}

Export:
- GET /meetings/{meeting_id}/export.json
- GET /meetings/{meeting_id}/export.md

Health endpoint:
- GET /health

## AI Prompt Architecture (MVP)
Recommended pipeline:
1. Structured extraction
- Prompt to extract decisions and tasks in strict JSON
- Fields: title, description, owner_name, due_date, priority, confidence
- If owner or date is unclear, return null

2. Meeting summary
- Prompt for a short executive summary
- Sections: context, decisions, actions, risks

Quality controls:
- JSON schema validation in backend
- Retries for invalid responses
- Prompt versioning in ai_runs

## Minimal Frontend Structure
frontend/
- app/
- app/page.tsx
- app/meetings/new/page.tsx
- app/meetings/[id]/page.tsx
- components/
- lib/

MVP frontend goal:
- Simple form for transcript/notes/recording
- Processing progress view
- Results view with summary + tasks + export

## Clear Implementation Plan
1. Foundation setup
- Configure FastAPI, PostgreSQL, and environment variables
- Define base backend and frontend structure

2. Data layer
- Model MVP tables in SQLAlchemy
- Create initial migrations with Alembic

3. AI processing
- Implement task_extraction_service
- Implement summary_service
- Persist outputs and audit data in ai_runs

4. API endpoints
- Create meetings, tasks, and export routes
- Validate payloads with Pydantic

5. Frontend experience
- Create new meeting flow
- Show results and edit task status

6. QA and hardening
- Test critical endpoints
- Add basic error handling and logging

7. Release MVP
- Deploy to staging environment
- Validate with pilot teams

## Constraints
- Focus on MVP only
- Avoid over-engineering
- Optimize development speed

## Goal
Have a clear implementation plan and a backend API ready to build MeetingTasks iteratively and at scale.
