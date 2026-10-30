# AI Troubleshooting & RAG Design (Phase 3 — not yet implemented)

This document designs the AI troubleshooting assistant and equipment
manual knowledge base from the spec (sections 4–5). **No code in this
repository implements this yet.** Phase 1 only ships the deterministic,
non-AI equipment-history summary (`GET /equipment/{id}/history`), which
this design builds on top of without replacing.

## Goals and hard constraints

1. Never invent manual sections, page numbers, or device specs.
2. Every AI answer must distinguish three confidence levels:
   - **Verified manual instruction** — text retrieved from an indexed,
     admin-uploaded manual, with citation (manufacturer, model, doc title,
     version, page).
   - **General troubleshooting suggestion** — a standard diagnostic step
     not tied to a specific manual (e.g. "check the cable is seated").
   - **Unverified hypothesis** — a plausible-but-unconfirmed cause the
     model is suggesting, explicitly labelled as such.
3. If no reliable source exists for a claim, say so — never fabricate a
   citation to look authoritative.
4. Minimize AI cost: retrieve first, call the LLM only when retrieval
   finds relevant material or the question needs free-form reasoning the
   retrieved text can't answer; use small/cheap models for structuring
   tasks; cache aggressively.

## Pipeline

```
Engineer describes problem (text / voice transcript / photo caption)
        │
        ▼
1. Query normalization (strip PII, expand common abbreviations
   e.g. "EQ" -> equipment model, using a small local lookup table)
        │
        ▼
2. Retrieval: vector search over indexed manual chunks, filtered to
   the company's own knowledge base + shared manufacturer manuals,
   filtered further to the equipment's manufacturer/model if known
        │
        ▼
3. If retrieval returns relevant chunks (similarity above threshold):
     -> Build a prompt that includes ONLY the retrieved chunks as
        source material, with explicit instructions to cite them and
        to say "not found in available manuals" rather than guess
   Else:
     -> Skip the LLM call entirely for the "verified" tier; offer only
        general troubleshooting suggestions from a static rules file
        (see "Deterministic fallback" below) plus an explicit
        unverified-hypothesis option if the engineer asks for one
        │
        ▼
4. LLM call (OpenAI-compatible API, or local Ollama for cost-sensitive
   deployments) returns a structured response:
   { possible_causes, diagnostic_steps, required_checks,
     relevant_settings, citations[], safety_notes, confidence_tier }
        │
        ▼
5. Post-processing: reject/flag any citation the retrieval step didn't
   actually return (prevents the model hallucinating a page number even
   when told not to); strip or escalate any instruction matching the
   safety blocklist (bypassing interlocks, disabling protective systems,
   live electrical work without a qualification disclaimer)
        │
        ▼
6. Response shown to engineer with the three-tier labelling, and logged
   (prompt + retrieved chunk IDs + response) for audit and for the
   "ai_requests_used_this_month" quota counter
```

## Document ingestion (manual knowledge base)

- Admin uploads a PDF (installation guide, service manual, SOP, etc.)
  through the web dashboard (not yet built).
- Extraction: PDF text extraction (e.g. `pypdf`/`pdfplumber`), falling
  back to OCR only for scanned pages.
- Chunking: split by heading/page boundaries, not fixed character counts,
  so a chunk corresponds to a coherent manual section and can be cited by
  page number accurately.
- Metadata preserved per chunk: manufacturer, model, document title,
  version, publication date, page number, source URL (if the admin
  provided one), and the company_id that owns the upload (shared
  manufacturer manuals are globally indexed; company SOPs stay
  tenant-scoped).
- Embeddings stored in a vector column/table (pgvector on Postgres, or a
  lightweight local index for SQLite dev) keyed to the chunk.
- Re-indexing is idempotent by (document_id, chunk_index) so re-uploading
  a corrected PDF doesn't duplicate chunks.

## Equipment maintenance history + AI (Phase 4 overlap)

Phase 1 already computes incident counts and repeated-description
detection deterministically (no AI, no hallucination risk — see
`app/routers/equipment.py:get_equipment_history`). Phase 4's AI layer adds
a narrative summary *on top of* those facts, with every sentence traceable
to a specific `maintenance_records` row, and is rendered as a separate
"AI-generated hypothesis" section so it can never be confused with the
logged facts above it.

## Cost controls (spec section 13)

- Retrieval always runs before any LLM call; a question answerable purely
  from retrieved text plus deterministic formatting never needs a "smart"
  model.
- Use a small/cheap model for structuring tasks (e.g. turning a transcript
  into report sections) and reserve a larger model only for the
  troubleshooting reasoning step.
- Per-company monthly AI request quota (already modeled in
  `app/config.py:PLAN_LIMITS` and reported via `/companies/me/usage`);
  Phase 3+ will make the backend actually block requests once a company's
  `ai_requests_used_this_month` hits its plan limit, returning a clear
  "upgrade your plan" error rather than silently degrading quality.
- Response caching keyed on (equipment model, normalized symptom text) so
  repeated reports of the same common fault don't re-run retrieval + LLM.

## Safety (spec section 16)

A static blocklist/ruleset (not LLM-judged) intercepts any step suggesting
bypassing an interlock, disabling a protective system, or performing
electrical/safety-critical work without a "qualified personnel only"
disclaimer. Matches are either rewritten to the disclaimer-added safe form
or, for clearly dangerous categories (e.g. "bypass the elevator door
interlock"), replaced entirely with an escalation message directing the
engineer to a qualified specialist/supervisor.
