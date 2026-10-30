# NightBrew FieldOps AI - Mobile (Flutter)

Phase 1 MVP mobile client: login, work order list (with offline cache),
work order detail with structured service notes, and work order creation.

## Status: code written, NOT build-verified

This container has no Flutter SDK installed, so this code has **not** been
run through `flutter pub get`, `flutter analyze`, or `flutter test`. It
follows standard Flutter/Dart syntax and the `http`/`sqflite`/
`connectivity_plus` package APIs as documented, but treat it as a reviewed
first draft, not a verified build, until someone runs it locally or in CI
with the Flutter SDK.

## Running locally (once you have the Flutter SDK)

```bash
flutter pub get
flutter run -d <device>
```

Point the app at your backend by editing `kDefaultApiBaseUrl` in
`lib/main.dart` (defaults to `http://localhost:8000`, matching the backend's
default dev server).

## What's implemented

- `lib/models/models.dart` - data models mirroring the backend's Pydantic schemas.
- `lib/services/api_client.dart` - REST client (login, customers, work orders, notes, reports).
- `lib/services/local_db.dart` - sqflite cache + offline write queue.
- `lib/services/sync_manager.dart` - drains the offline queue, detects
  update conflicts by comparing `updated_at` timestamps (never silently
  overwrites a newer server record).
- `lib/screens/` - login, work order list (shows an offline banner when
  there's no connectivity and cached data is being shown), work order
  detail (add service notes, queued offline if needed), create work order.

## Not implemented in this pass

- Photo capture/annotation, voice-to-text, AI troubleshooting chat, manual
  RAG search, PDF/DOCX viewing in-app, customer/site/equipment management
  screens, push notifications, biometric login. See ROADMAP.md at the repo
  root for phased follow-up work.
