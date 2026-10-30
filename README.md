# NightBrew FieldOps AI

AI Field Service Engineer Copilot + Field Service Management.

Helps field engineers (AV/VC, IT, HVAC, electrical, elevator, factory
maintenance, and other technical service industries) troubleshoot
equipment, record maintenance activity, and generate professional service
reports — with offline-first mobile operation and multi-company (tenant)
isolation.

## Current state: Phase 1 MVP (working, tested)

This repository currently implements **Phase 1** of the roadmap in
ROADMAP.md: a real, runnable, tested backend plus a mobile app skeleton.
Phases 2–6 (AI troubleshooting/RAG, voice-to-text, maintenance
intelligence, production billing, store releases) are designed in the docs
below but **not yet implemented in code**. See "What's implemented" below
and ROADMAP.md for the honest line between done and planned.

## What's implemented

**Backend** (`backend/`) — FastAPI + SQLAlchemy + SQLite (swap to Postgres
via `DATABASE_URL`), fully working and covered by 16 passing pytest tests:

- Multi-company signup/login with JWT auth and 5 roles (owner, admin,
  supervisor, engineer, viewer), enforced via RBAC dependencies.
- Company-scoped data isolation (every query filters by `company_id`;
  cross-tenant access returns 404, not 403, to avoid leaking existence).
- Customers, sites, rooms, equipment inventory.
- Work orders with the full status lifecycle (open → assigned → in
  progress → waiting for parts / pending customer → completed → closed),
  priority, and engineer assignment.
- Structured service notes (Initial Condition / Investigation / Outcome /
  Follow Up / General) attached to work orders.
- Equipment maintenance history with a deterministic (non-AI) summary:
  total incident count and repeated-description detection, clearly labelled
  as facts, not AI hypotheses.
- Service report generation as both PDF (reportlab) and DOCX (python-docx).
  Any field the engineer hasn't filled in is rendered as
  `[REQUIRES ENGINEER CONFIRMATION]` — nothing is fabricated.
- A mock subscription/usage endpoint (`/companies/me/usage`) reflecting the
  Starter/Pro/Enterprise plan limits in COMMERCIAL_PLANS.md. Not wired to a
  real payment processor.
- An audit log table recording create/update/generate actions.

**Mobile** (`mobile/`) — Flutter source for login, an offline-aware work
order list (cached in SQLite, with a visible offline banner), work order
detail with service-note entry (queued locally if offline), and work order
creation. **This code has not been built or run** — there is no Flutter SDK
in the environment this was written in. Treat it as a reviewed first draft;
run `flutter pub get && flutter analyze` before trusting it. See
`mobile/README.md`.

**Not implemented yet**: web admin dashboard, AI troubleshooting assistant,
manual/RAG knowledge base, voice-to-text, photo management, real billing,
Android/iOS release builds. These are designed in the docs listed below.

## Documentation

- `ARCHITECTURE.md` — system architecture, components, data flow.
- `ROADMAP.md` — phased plan and what's done vs. planned.
- `DATABASE_SCHEMA.md` — entity-relationship description of the schema.
- `AI_RAG_DESIGN.md` — design for the Phase 3 troubleshooting/RAG system
  (not yet built).
- `OFFLINE_SYNC_DESIGN.md` — offline queue and conflict-resolution design.
- `SECURITY.md` — auth, isolation, safety rules for AI-generated guidance.
- `COST_ESTIMATE.md` — rough operating cost at a few customer scales.
- `COMMERCIAL_PLANS.md` — Starter/Pro/Enterprise plan definitions.
- `DEPLOYMENT.md` — how to run the backend locally and deploy it.
- `LICENSE_AUDIT.md` — licenses of every third-party dependency used.

## Quick start (backend)

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API docs. Run the test
suite with:

```bash
cd backend
./venv/bin/pytest -q
```

16/16 tests pass as of this commit (work order creation/lifecycle,
structured notes, equipment history, report generation and missing-field
handling, company data isolation, role permissions, subscription usage
limits).
