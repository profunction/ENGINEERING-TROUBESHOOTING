# Roadmap

Status key: ✅ done and tested · 🚧 designed, not built · ⬜ not started

## Phase 1 — MVP Foundation

- ✅ FastAPI backend (auth, RBAC, company isolation)
- ✅ SQLite local database (swaps to Postgres via `DATABASE_URL`)
- ✅ Customer / site / room management
- ✅ Equipment inventory + maintenance record logging
- ✅ Work order creation, assignment, status lifecycle
- ✅ Structured manual service notes (Initial Condition / Investigation /
  Outcome / Follow Up)
- ✅ Basic PDF service reports (+ DOCX, which the spec asks for later but
  was cheap to add alongside PDF)
- 🚧 Flutter mobile application — code written (login, work order list w/
  offline cache, detail, create), **not build-verified** (no Flutter SDK
  available in the environment this was built in)
- ⬜ React web admin dashboard

## Phase 2 — AI Service Reports

- ⬜ Voice transcription (speech-to-text)
- ⬜ AI note structuring (turning a raw transcript into Initial
  Condition/Investigation/Outcome/Follow Up sections)
- ⬜ AI-assisted report drafting (still requires engineer review/edit before
  finalizing — the generator will keep marking anything unconfirmed rather
  than inventing content)
- ⬜ Photo attachment UI + storage wiring
- ✅ PDF/DOCX export (built ahead of schedule in Phase 1, since the
  deterministic renderer didn't depend on the AI pieces)

## Phase 3 — AI Troubleshooting

- ⬜ Manual upload pipeline (PDF ingestion, text extraction, chunking)
- ⬜ Document indexing (embeddings + vector store)
- ⬜ RAG retrieval (symptom → relevant manual chunks)
- ⬜ AI troubleshooting endpoint, with mandatory source citations and a
  three-way confidence label (verified manual instruction / general
  troubleshooting suggestion / unverified hypothesis) — see AI_RAG_DESIGN.md
- ⬜ Safety gating: refuse unsafe instructions (bypassing interlocks,
  electrical work without qualification disclaimer), escalate dangerous
  faults rather than answer them

## Phase 4 — Maintenance Intelligence

- ✅ Equipment history data model + deterministic incident/repeat summary
  (built in Phase 1 since it required no AI — see
  `GET /equipment/{id}/history`)
- ⬜ AI-generated narrative summary layered on top of the deterministic
  facts, explicitly labelled as hypothesis (not fact)
- ⬜ Cross-equipment pattern detection (e.g. "this firmware version
  correlates with more call-backs across sites")
- ⬜ Historical AI search ("what happened to similar units at other sites?")

## Phase 5 — Business Operations

- ✅ Multi-company accounts + company data isolation (Phase 1)
- ✅ Engineer assignment (Phase 1, via `assigned_engineer_id`)
- ⬜ Supervisor dashboard (web)
- 🚧 Offline queue + sync design done (OFFLINE_SYNC_DESIGN.md) and
  implemented client-side in the (unverified) Flutter app; needs a matching
  server-side batch-sync endpoint for efficiency at scale
- ⬜ Customer signatures captured on-device (schema already supports
  `engineer_signature_name` / `customer_signature_name` text fields; needs
  an actual signature-capture widget and image storage)

## Phase 6 — Commercial Release

- 🚧 Subscription architecture — plan tiers and limits defined
  (COMMERCIAL_PLANS.md, `app/config.py:PLAN_LIMITS`) and a read-only usage
  endpoint exists; no real payment processor integration (mock only, as the
  spec requests for the MVP)
- ⬜ Usage limit *enforcement* (currently reported, not yet blocking)
- ⬜ S3-compatible cloud storage (currently local disk)
- ⬜ Production-grade auth hardening (refresh tokens, rate limiting, audit
  log review UI — the audit log table itself already exists)
- ⬜ Android release build
- ⬜ iOS release build
- ⬜ Web administration dashboard

## Honest summary

Everything marked ✅ above is implemented and covered by the 16 passing
backend tests. Everything marked 🚧 has a concrete design and, where noted,
partial/unverified code. Everything marked ⬜ exists only as a plan in this
document and the other design docs — there is no code for it yet.
