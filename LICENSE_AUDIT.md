# License Audit

All third-party dependencies currently used by Phase 1, as installed in
`backend/venv` for the backend and declared in `mobile/pubspec.yaml` for
the mobile app. All are permissive licenses (MIT/BSD/Apache-2.0) compatible
with commercial, closed-source use. **Recommendation**: re-run this audit
(e.g. with `pip-licenses` and `flutter pub deps --json` + a license
checker) immediately before any commercial release, since dependency
versions and their licenses can change over time — this document reflects
a point-in-time check.

## Backend (Python)

| Package | License | Commercial use |
|---|---|---|
| fastapi | MIT | ✅ |
| uvicorn | BSD-3-Clause | ✅ |
| SQLAlchemy | MIT | ✅ |
| pydantic | MIT | ✅ |
| pydantic-settings | MIT | ✅ |
| email-validator | Unlicense (public domain) | ✅ |
| python-jose | MIT | ✅ |
| passlib | BSD-3-Clause | ✅ |
| bcrypt | Apache License 2.0 | ✅ |
| python-multipart | Apache License 2.0 | ✅ |
| reportlab | BSD-style (ReportLab's own license, see its `license.txt`) | ✅ for the open-source `reportlab` toolkit used here. Note: ReportLab also sells a separate commercial "PLUS" product with more features — this project uses only the free/open-source package, not PLUS. |
| python-docx | MIT | ✅ |
| pytest | MIT | ✅ (dev/test dependency only, not shipped) |
| httpx | BSD-3-Clause | ✅ (dev/test dependency only, not shipped) |

No GPL, AGPL, or other copyleft-licensed backend dependency is used.

## Mobile (Flutter/Dart)

Declared in `mobile/pubspec.yaml`. These are the commonly-known licenses
for these packages' publishers at the time of writing; **verify current
license text for the exact resolved versions** once `flutter pub get` has
actually been run (not done in this pass — no Flutter SDK available, see
`mobile/README.md`), since this list was not generated from a resolved
lockfile.

| Package | Typical license | Notes |
|---|---|---|
| flutter (SDK) | BSD-3-Clause | Google |
| http | BSD-3-Clause | dart.dev team |
| sqflite | BSD-3-Clause / MIT | tekartik |
| path | BSD-3-Clause | dart.dev team |
| provider | MIT | community (rrousselGit) |
| shared_preferences | BSD-3-Clause | flutter.dev plugin |
| uuid | MIT | community |
| connectivity_plus | BSD-3-Clause | fluttercommunity |
| image_picker | BSD-3-Clause / Apache-2.0 | flutter.dev plugin |
| intl | BSD-3-Clause | dart.dev team |
| flutter_lints | BSD-3-Clause | Google (dev dependency only) |

## Manufacturer manuals (spec section 5)

Not a software license issue, but noted here per the spec's explicit
requirement: equipment manuals (Cisco, Poly, Crestron, Extron, Q-SYS,
Logitech, Bosch DICENTIS, Dante, BrightSign, Maxhub, etc.) are each
manufacturer's copyrighted material. This application does **not**
automatically download or redistribute such manuals — Phase 3's design
(AI_RAG_DESIGN.md) only indexes manuals an authorized admin explicitly
uploads, for that admin's own company's internal use. Before any feature
that shares indexed manual content *across* companies (e.g. a shared
manufacturer-manual library), get explicit legal review of each
manufacturer's documentation license/terms of use.

## Action items before commercial release

1. Re-run a dependency license scan against the actual locked versions
   (`requirements.txt` pins exact versions already; add a lockfile-based
   scan step in CI).
2. Confirm `mobile/pubspec.lock` (generated once `flutter pub get` runs)
   licenses match this table.
3. Get explicit confirmation from legal/ops on manufacturer manual
   redistribution terms before Phase 3 ships to more than one company.
