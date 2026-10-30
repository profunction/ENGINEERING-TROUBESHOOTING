# Security

## Implemented in Phase 1

- **Authentication**: JWT bearer tokens (`python-jose`), 8-hour default
  expiry (`ACCESS_TOKEN_EXPIRE_MINUTES`, configurable). Passwords hashed
  with bcrypt via `passlib`; plaintext passwords are never stored or
  logged.
- **Company (tenant) data isolation**: every business table carries a
  `company_id`; every lookup in `app/deps.py:get_company_scoped_or_404`
  filters by the authenticated user's `company_id` and returns 404 (not
  403) for another tenant's row, so a tenant can't even confirm another
  tenant's record exists. There is no endpoint that accepts a client-
  supplied `company_id` — it is always derived from the verified JWT.
  Covered by `backend/tests/test_company_isolation.py`.
- **Role-based access control**: 5 roles (owner > admin > supervisor >
  engineer > viewer), enforced via `require_role(...)` FastAPI
  dependencies on every mutating endpoint. Covered by
  `backend/tests/test_permissions.py`.
- **Audit logging**: `audit_logs` table records create/update/generate
  actions with company_id, user_id, action, entity type/id, and
  timestamp. (A review UI for this log is not yet built — Phase 6.)
- **Report integrity**: the service report generator never fabricates
  diagnostic actions, parts, or outcomes; any missing required field is
  rendered as `[REQUIRES ENGINEER CONFIRMATION]` rather than guessed.

## Designed but not yet implemented

- **Encrypted communication**: the backend should run behind TLS
  (terminated at a reverse proxy/load balancer in deployment — see
  DEPLOYMENT.md); the app code itself doesn't terminate TLS.
- **Secure file storage**: Phase 1 stores generated reports on local disk
  under `backend/storage/`; production should use an S3-compatible bucket
  with server-side encryption and signed, time-limited download URLs
  rather than the current direct `FileResponse`.
- **API rate limiting**: not implemented. Recommended: a reverse-proxy
  level limiter (e.g. per-IP and per-user-token) ahead of Phase 6.
- **Data retention settings**: no automatic purge/retention policy exists
  yet; company-configurable retention (spec section 16) is Phase 6 work.
- **Cloud AI consent**: no AI calls exist yet (Phase 3), so there is no
  consent flow to build yet; AI_RAG_DESIGN.md requires one before any
  cloud LLM call ships.
- **Refresh tokens / token revocation**: current JWTs are stateless bearer
  tokens with a fixed expiry and no revocation list; logout is
  client-side only (discard the token). A production hardening pass
  should add refresh tokens and a revocation mechanism for
  compromised-device scenarios.

## AI safety rules (apply once Phase 3 ships — see AI_RAG_DESIGN.md)

These are requirements for code that does not exist yet, documented now so
they're designed in from the start rather than retrofitted:

- Never fabricate manufacturer instructions, manual sections, page
  numbers, or device specifications.
- Every AI response must separate verified manual citations, general
  troubleshooting suggestions, and unverified hypotheses.
- Instructions involving bypassing interlocks or disabling protective
  systems must be blocked or rewritten to escalate to a qualified
  specialist, never answered directly.
- Electrical or other safety-critical work must carry a "qualified
  personnel only" disclaimer; the system must not present itself as a
  substitute for that qualification.
- Potentially dangerous faults (described in AI_RAG_DESIGN.md's safety
  blocklist) are escalated, not diagnosed by the model alone.

## Reporting a vulnerability

This is an internal MVP repository; there is no public disclosure process
yet. Routing security concerns to the repository owner directly is
appropriate at this stage.
