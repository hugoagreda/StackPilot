# StackPilot Architecture

## Objective
StackPilot is a micro-SaaS platform for launching and operating multiple independent products with minimal setup friction.

## Core Principles
- Central control dashboard for operations and visibility
- Independent micro-products with isolated business logic
- Shared infrastructure services to avoid duplicated work

## Product Boundaries
Each product inside `apps/` should own:
- Frontend
- Backend
- Database
- Product-specific domain logic

Products must be deployable and maintainable without requiring cross-product code changes.

## Shared Services
The `core/` layer provides cross-cutting services:
- Authentication
- Billing
- Analytics
- Notifications
- Shared utility modules

These services should expose clear interfaces and avoid product-specific assumptions.

## Platform Layers
- `dashboard/`: Central control plane for team operations and product monitoring
- `packages/`: Reusable packages (UI components, API client, shared types)
- `infra/`: Docker, deployment templates, and infrastructure scripts
- `docs/`: Architecture and onboarding documentation

## Scaling Model
To launch a new product:
1. Duplicate or generate from `apps/template-app`
2. Wire in shared services from `core/`
3. Add product routes to `dashboard/`
4. Configure deployment in `infra/deployment`

This model enables repeatable product launches with low operational overhead.
