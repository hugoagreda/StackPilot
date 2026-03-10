# Rental Price Estimator

Rental Price Estimator is a micro-SaaS to estimate the monthly rental value of a property.
The product focus is smart, fast, and explainable pricing to improve rental decisions.

## Role
This repository is implemented with a focus on:
- Data science applied to real estate analytics
- SaaS product architecture

## Project Context
The user enters property characteristics and the system returns a rental estimate.

Main inputs:
- city
- neighborhood
- square_meters
- bedrooms
- bathrooms
- condition
- furnished

System outputs:
- estimated_rent
- market_price_range
- price_per_sqm
- demand_level

## Target Users
- Property owners
- Real estate investors
- Landlords
- Real estate agencies

## Core Value
Help users define an optimal rental price using market data, comparables, and clear adjustment rules.

## MVP Scope
MVP scope only, avoiding over-engineering and prioritizing development speed.

Includes:
- Property input form
- Rent estimation algorithm
- Comparable listings
- Simple report

## Tech Stack
- Backend: FastAPI
- Frontend: React
- Database: PostgreSQL

## Data Sources
Potential data sources:
- Real estate listings
- Public datasets
- Scraping pipelines

## Required Architecture
Modular backend architecture:

- backend/app/api: HTTP layer and endpoint versioning
- backend/app/services: business logic and estimation calculations
- backend/app/models: SQLAlchemy entities
- backend/app/schemas: input/output DTOs
- backend/app/core: configuration, DB, and wiring

### Micro structure
- backend: API FastAPI
- frontend: web client for form and results
- database: SQL schema and migrations
- config: environment configuration
- docs: architecture and decisions
- tests: MVP tests

Python environment note:
- Current virtual environment in backend/.venv
- Python dependencies in backend/requirements.txt

## Database Schema (MVP)
Main entities:
- cities
- neighborhoods
- properties
- listings_raw
- estimates
- estimate_comparables
- market_stats_monthly

Key relationships:
- city 1:N neighborhoods
- neighborhood 1:N properties
- property 1:N estimates
- estimate N:N listings_raw (via estimate_comparables)

Recommended minimum fields:
- properties: id, city_id, neighborhood_id, square_meters, bedrooms, bathrooms, condition, furnished, created_at
- listings_raw: id, source, external_id, city_id, neighborhood_id, square_meters, bedrooms, bathrooms, condition, furnished, listed_rent, listing_date
- estimates: id, property_id, estimated_rent, lower_range, upper_range, price_per_sqm, demand_level, confidence_score, model_version, created_at

## Estimation Algorithm Approach (MVP)
Recommended pipeline:
1. Comparable retrieval
- Filter comparables by city and neighborhood
- Restrict by similarity in size, bedrooms, and bathrooms
- Prioritize recent listings

2. Similarity scoring
- Weighted distance score using:
- square_meters
- bedrooms
- bathrooms
- condition
- furnished

3. Price estimation
- Base estimate using weighted median of comparables
- Adjustments by condition and furnished status
- price_per_sqm calculation

4. Market range and demand
- lower_range and upper_range using comparable percentiles
- demand_level based on inventory, absorption speed, and price trend

## Backend API Design (MVP)
Suggested base path: /api/v1

Estimates:
- POST /estimates
- GET /estimates/{estimate_id}
- GET /estimates/{estimate_id}/comparables
- GET /estimates/{estimate_id}/report

Market:
- GET /markets/cities
- GET /markets/neighborhoods?city_id={city_id}
- GET /markets/stats?city_id={city_id}&neighborhood_id={neighborhood_id}

Health endpoint:
- GET /health

## MVP Architecture
Components:
- React frontend for input, results, and report
- FastAPI backend for validation, comparables, and estimation
- PostgreSQL for properties, listings, and market aggregates
- Batch pipeline for data ingestion and normalization

Main flow:
1. User completes the property form.
2. API validates input and searches for comparables.
3. Estimation service calculates estimated_rent and market range.
4. API returns the result with price_per_sqm, demand_level, and comparables.

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
- Prepare ingestion process for listings

3. Estimation service
- Implement comparable search
- Implement similarity scoring
- Implement estimation and market range logic

4. API endpoints
- Create estimates and market routes
- Validate payloads with Pydantic

5. Frontend experience
- Build input form
- Show results, comparables, and a simple report

6. QA and hardening
- Test critical endpoints
- Add basic error handling and logging

7. Release MVP
- Deploy to staging environment
- Validate with pilot users

## Constraints
- Focus on MVP only
- Avoid over-engineering
- Optimize development speed

## Goal
Have a clear implementation plan, a backend API ready to scale, and a product foundation to estimate rent in a reliable and explainable way.
