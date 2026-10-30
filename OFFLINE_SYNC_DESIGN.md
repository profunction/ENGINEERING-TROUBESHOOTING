# Offline Mode & Sync Design

Client-side implementation status: written in `mobile/lib/services/local_db.dart`
and `mobile/lib/services/sync_manager.dart`, **not build-verified** (no
Flutter SDK available when this was written — see `mobile/README.md`).
Server-side batch sync endpoint described below is **not yet built**; the
current server API handles one record at a time, which is correct but not
yet optimized for syncing many queued changes at once.

## What must work offline (spec section 12)

- Viewing assigned work orders (cached locally).
- Accessing cached equipment details.
- Writing service notes.
- Taking photos (captured to local storage; upload deferred — not yet
  wired in this pass).
- Recording maintenance activities.
- Generating a basic report *draft* locally where practical (full PDF/DOCX
  rendering currently happens server-side only; a fully offline renderer is
  future work, tracked in ROADMAP.md Phase 2/5).

Cloud AI troubleshooting is explicitly unavailable offline and the UI must
say so (implemented as the orange "Offline mode" banner in
`work_order_list_screen.dart`).

## Local storage model

SQLite tables (via `sqflite`):

- `cached_customers`, `cached_work_orders`, `cached_equipment` — last
  known-good snapshot from the server, each row storing the full JSON
  payload plus a `synced_at` timestamp. `cached_work_orders` additionally
  stores `updated_at` separately (indexed) so sync can compare it without
  deserializing JSON.
- `pending_changes` — an append-only queue of local writes:
  `(local_id, entity_type, entity_id, operation, payload, base_updated_at,
  created_at, status)`. `status` is one of `pending`, `applied`,
  `conflict`. Nothing is deleted from this table automatically; a
  resolved conflict is a deliberate user action, not a silent retry.

## Why `base_updated_at` matters

Every queued **update** (not create) records the `updated_at` timestamp
of the row as it existed on the device when the engineer made the edit.
This is the basis for the conflict rule below.

## Sync algorithm

Triggered when connectivity returns (via `connectivity_plus`) and on pull-
to-refresh:

1. For each `pending` row in `pending_changes`, oldest first:
   - **Create** operations are applied directly — there is no prior server
     state to conflict with. (A duplicate-create edge case, e.g. the same
     offline work order queued twice due to a UI bug, is out of scope for
     Phase 1 and would need idempotency keys; noted as a known gap.)
   - **Update** operations first re-fetch the current server row. If the
     server's `updated_at` is **after** the queued change's
     `base_updated_at`, the server row changed since this edit was made —
     the queued change is marked `conflict`, **not applied**, and surfaced
     to the user. It is never silently discarded or silently applied over
     a newer record.
   - If the server row is not newer, the queued payload is PATCHed to the
     server, and on success the row is marked `applied`.
2. After the queue drains (or in parallel), a fresh `GET /work-orders` is
   pulled and the local cache is replaced with the server's current view,
   so the device converges on server state for anything that wasn't in
   conflict.
3. Changes marked `conflict` stay visible until a human resolves them
   (keep local version / keep server version / manually merge) — there is
   no automatic resolution, per the spec's explicit requirement.

## What's intentionally not solved yet

- **Server-side batch sync endpoint.** Right now each queued change is
  sent as an individual REST call when connectivity returns, which is
  correct but inefficient for an engineer who was offline all day with
  dozens of queued notes. A future `/sync/batch` endpoint accepting an
  array of operations (and returning per-operation success/conflict) would
  reduce round trips; the client-side queue format above was designed to
  translate directly into that endpoint's request body without a schema
  change.
- **Photo upload queuing** uses the same `pending_changes` table shape in
  principle, but the capture-and-queue flow isn't implemented in this pass.
- **Offline report rendering.** PDF/DOCX generation requires the server
  today; a fully offline-capable report draft (plain text/structured JSON
  only, finalized when back online) is listed in ROADMAP.md.
