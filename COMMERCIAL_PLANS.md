# Commercial Plans

Mock billing for the MVP, as the spec requires (section 15). Plan
definitions live in code at `backend/app/config.py:PLAN_LIMITS`, not hard-
coded in UI strings, so changing a limit or adding a plan doesn't require
touching multiple files. **No real payment processor is integrated** —
`subscription_plan` is just a field on the company, settable at signup
time (currently always `starter` by default) with no payment flow behind
it.

## Plan tiers

| Plan | Price (suggested) | AI requests/month | Stored reports | Storage |
|---|---|---|---|---|
| Starter | RM49/engineer/month | 200 | 500 | 2 GB |
| Pro | RM99/engineer/month | 2,000 | 5,000 | 20 GB |
| Enterprise | Custom quotation | Unlimited (custom) | Unlimited (custom) | Unlimited (custom) |

Prices are suggested starting points from the product spec, not finalized
pricing — they live only in this document and are not hard-coded into the
application beyond the `PLAN_LIMITS` dict's *limits* (not prices; the
backend doesn't currently model price at all, only usage caps, since no
billing integration exists yet).

## What differs by plan today

- `ai_requests_per_month` — reported (not yet enforced) via
  `GET /companies/me/usage`.
- `stored_reports` / `storage_mb` — defined in `PLAN_LIMITS` but not yet
  checked anywhere in the API (no endpoint currently blocks creating a
  report or uploading a file based on these limits). This is flagged
  explicitly in ROADMAP.md Phase 6 as "reported, not yet enforced."

## Planned differentiators (not yet built)

- Advanced maintenance analytics (Phase 4) — likely Pro/Enterprise only.
- Company-specific knowledge bases (Phase 3) — likely available on all
  plans but with a larger manual-storage allowance on higher tiers.
- External integrations (e.g. ticketing system sync) — likely
  Enterprise-only given the custom integration work involved.
- Support level (email vs. dedicated) — a business/process commitment,
  not something the application code enforces.

## Upgrading from mock to real billing

Production billing requires a trusted backend integration (e.g. Stripe or
a regional payment gateway) that:

1. Owns the source of truth for `subscription_plan` and payment status
   (webhook-driven, not client-settable).
2. Updates `companies.subscription_plan` only from verified webhook
   events, never from a client API call.
3. Actually enforces `PLAN_LIMITS` at the point of use (reject the
   mutating call, don't just report usage after the fact).

None of this exists in Phase 1; `subscription_plan` can currently only be
set implicitly (defaults to `starter`) and there's no endpoint to change
it, which is intentional — it prevents a tenant from "upgrading" itself
for free until real billing is wired in.
