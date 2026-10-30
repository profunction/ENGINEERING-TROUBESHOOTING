# Cost Estimate

Rough, order-of-magnitude figures for running the Phase 1 MVP (field
service management only — no AI costs yet, since Phase 3 isn't built).
All figures are illustrative planning estimates, not quotes.

## Phase 1 (current code): infrastructure only

| Item | Small deployment (~5 companies, ~30 engineers) | Notes |
|---|---|---|
| App server (FastAPI container) | 1 small VM/container (1-2 vCPU, 1-2GB RAM) | FastAPI + SQLite/Postgres is light; this workload doesn't need autoscaling at this size |
| Database | Managed Postgres, smallest tier, or self-hosted on the same VM | SQLite is fine for a single-node pilot; move to Postgres once >1 app instance or real concurrency matters |
| File storage (reports, future photos) | S3-compatible bucket, pay-per-GB | Reports are small (a few hundred KB each); the real driver will be photo volume once that ships |
| TLS/reverse proxy | Free (Let's Encrypt + nginx/Caddy) or included with most PaaS | |
| **No AI cost in Phase 1** | $0 | The report generator is deterministic (reportlab/python-docx), not an LLM call |

A single small VM plus a managed small-tier Postgres instance is enough
to run Phase 1 for a pilot customer base; this is a double-digit-dollars-
per-month order of magnitude, not hundreds, before any AI usage.

## Phase 3+ (projected AI cost, once built)

AI cost will scale with:

- **Retrieval-first design** (AI_RAG_DESIGN.md): most troubleshooting
  questions should be answerable from retrieved manual text plus
  deterministic formatting, with the LLM call reserved for genuine
  reasoning over that retrieved context — not for every message.
- **Small model for structuring tasks** (e.g. voice note → structured
  report sections), larger model only for the troubleshooting reasoning
  step.
- **Per-company monthly quota** (see COMMERCIAL_PLANS.md /
  `app/config.py:PLAN_LIMITS`) caps worst-case spend per tenant.
- Embeddings for manual indexing are a one-time cost per document (re-run
  only when a document is re-uploaded), not a per-query cost.

Actual per-request $ figures depend on which model/provider is chosen at
build time and change frequently; this document intentionally avoids
quoting specific per-token prices that would go stale. When Phase 3 is
implemented, token usage should be tracked per company (the
`ai_requests_used_this_month` counter already exists for this) and
reconciled against actual provider invoices to produce a real number.

## Cost-control features already in the data model

- `companies.ai_requests_used_this_month` — ready for Phase 3 to
  increment per AI call.
- `app/config.py:PLAN_LIMITS` — per-plan monthly AI request allowance,
  storage allowance, and stored-report allowance, read by
  `/companies/me/usage` today (reporting only; enforcement is Phase 6
  work, see ROADMAP.md).

## What drives cost up, and the mitigations already designed

| Cost driver | Mitigation (see AI_RAG_DESIGN.md / OFFLINE_SYNC_DESIGN.md) |
|---|---|
| Every field question hitting a large LLM | Retrieval-first; cache common symptom → answer pairs |
| Re-indexing manuals repeatedly | Idempotent chunking keyed by (document_id, chunk_index) |
| Large photo/video uploads | Deferred to Phase 2+; store at reasonable compression, not raw camera output |
| Many small sync round-trips from offline devices | Planned server-side batch sync endpoint (OFFLINE_SYNC_DESIGN.md) |
