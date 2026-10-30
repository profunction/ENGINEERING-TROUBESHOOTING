# Architecture

## Overview

NightBrew FieldOps AI is a multi-tenant field service management platform
with an AI troubleshooting copilot layered on top. Phase 1 (this
repository's current working code) delivers the field service management
core without the AI layer; later phases add AI troubleshooting, RAG over
equipment manuals, and maintenance intelligence on the same data model.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Flutter Mobile  │     │  React Web Admin │     │   Future: AI     │
│  (Android/iOS)   │     │  (not yet built)  │     │  Troubleshooting │
│  + local SQLite  │     │                   │     │  + RAG (Phase 3) │
└────────┬─────────┘     └─────────┬─────────┘     └────────┬────────┘
         │ REST/JSON over HTTPS    │                        │
         └────────────┬────────────┴────────────────────────┘
                       ▼
            ┌─────────────────────┐
            │   FastAPI backend    │
            │  - auth/RBAC         │
            │  - company isolation │
            │  - work order mgmt   │
            │  - report generator  │
            └──────────┬───────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   PostgreSQL/    S3-compatible   OpenAI-compatible
   SQLite (dev)   file storage    API (Phase 3+)
```

## Components

### Backend (`backend/`)

- **FastAPI** application (`app/main.py`) exposing a REST API.
- **SQLAlchemy** ORM models (`app/models.py`) — see DATABASE_SCHEMA.md.
- **Pydantic** schemas (`app/schemas.py`) for request/response validation,
  kept separate from ORM models so internal fields (e.g. `hashed_password`)
  are never serialized to clients.
- **JWT auth** (`app/security.py`) with a 5-level role hierarchy
  (owner > admin > supervisor > engineer > viewer) enforced via FastAPI
  dependency injection (`require_role(...)`).
- **Company isolation** (`app/deps.py`) — every multi-tenant lookup goes
  through `get_company_scoped_or_404`, which filters by `company_id` and
  returns 404 for rows belonging to another tenant (never 403, so tenants
  can't distinguish "not yours" from "doesn't exist").
- **Report generator** (`app/services/report_generator.py`) — deterministic
  PDF/DOCX rendering, no AI involved, so report generation cost is ~zero
  and output is reproducible.
- **Routers** (`app/routers/`) — one module per resource family
  (auth, companies, customers/sites/rooms, equipment, work orders +
  service notes, reports).

### Mobile (`mobile/`)

Flutter app (single codebase for Android + iOS). Architecture:

- `lib/models/` — plain Dart data classes mirroring backend schemas.
- `lib/services/api_client.dart` — REST client.
- `lib/services/local_db.dart` — sqflite cache of server data + an offline
  write queue (`pending_changes` table).
- `lib/services/sync_manager.dart` — drains the write queue when
  connectivity returns; see OFFLINE_SYNC_DESIGN.md for the conflict rule.
- `lib/screens/` — UI screens, intentionally thin (business logic lives in
  services so it's testable without widgets).

### Web admin dashboard

Not yet built. Planned as React + TypeScript, consuming the same FastAPI
backend, for company/user administration, work order supervision, manual
uploads (Phase 3), and billing administration (Phase 6).

### Data storage

- **Relational data**: PostgreSQL in production, SQLite for local dev and
  the mobile offline cache. The backend's `DATABASE_URL` env var switches
  between them with no code changes (see `app/config.py`).
- **Files** (photos, generated PDFs/DOCX, uploaded manuals): local disk in
  Phase 1 (`backend/storage/`), designed to move to S3-compatible object
  storage (e.g. MinIO self-hosted, or AWS S3 / Cloudflare R2) without
  changing the application layer — only the storage adapter changes.

### AI layer (Phase 3+, not yet built)

See AI_RAG_DESIGN.md. Planned to call an OpenAI-compatible API (cloud) or
a local Ollama model, gated behind retrieval so the LLM only ever answers
from retrieved manual text plus the user's described symptom — never from
unguided model memory about a specific device.

## Multi-tenancy model

One `companies` row per customer organization. Every business table
(`customers`, `sites`, `equipment`, `work_orders`, ...) carries a
`company_id` foreign key. There is no cross-company foreign key anywhere in
the schema, and no endpoint accepts a company_id from the client — it is
always derived from the authenticated user's JWT. This is enforced at the
query layer (see `app/deps.py`), not just the API layer, so a bug in one
router can't leak another tenant's rows.

## Why this stack

- **FastAPI + SQLAlchemy + SQLite/Postgres**: free, open-source, runs on a
  single small VM or container; no managed-service lock-in required for the
  MVP. See COST_ESTIMATE.md.
- **Flutter**: one codebase for Android + iOS, avoiding duplicate native
  development cost for a small team.
- **reportlab / python-docx**: pure-Python, no system dependencies (unlike
  e.g. wkhtmltopdf or LibreOffice headless), so report generation works in
  any container without extra OS packages.
