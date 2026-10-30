# Deployment

## Local development (backend)

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/uvicorn app.main:app --reload
```

The API is then at `http://localhost:8000`, interactive docs at
`http://localhost:8000/docs`. Default config uses a local SQLite file
(`backend/fieldops.db`) and local disk storage (`backend/storage/`) — both
are gitignored and created automatically on first run.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./fieldops.db` | Set to a Postgres URL (e.g. `postgresql://user:pass@host/db`) for staging/production |
| `SECRET_KEY` | `dev-secret-change-in-production` | JWT signing key — **must** be overridden in any non-local environment |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | JWT lifetime |
| `FILE_STORAGE_DIR` | `./storage` | Base directory for generated reports (and, later, photos/manuals) |

## Running tests

```bash
cd backend
./venv/bin/pytest -q
```

16 tests currently cover work order lifecycle, service notes, equipment
history, report generation (including missing-field handling), company
data isolation, role permissions, and subscription usage reporting.

## Production deployment (recommended path for Phase 1)

1. **Database**: provision a small managed PostgreSQL instance (or
   self-host). Set `DATABASE_URL` accordingly. SQLAlchemy's
   `Base.metadata.create_all()` (called on app startup) will create the
   schema on first run; for ongoing schema changes, introduce Alembic
   migrations before this goes further than a pilot (not yet set up in
   this repo).
2. **App server**: run the FastAPI app under a production ASGI server
   (`uvicorn` with `--workers`, or behind `gunicorn` with the uvicorn
   worker class) inside a container.
3. **Reverse proxy / TLS**: put nginx or Caddy (or your cloud provider's
   load balancer) in front for TLS termination and to add rate limiting
   (not yet implemented in the app itself — see SECURITY.md).
4. **File storage**: for anything beyond a single-node pilot, point
   `FILE_STORAGE_DIR`-equivalent logic at an S3-compatible bucket instead
   of local disk (requires a small code change in
   `app/services/report_generator.py` and the `FileResponse` download
   endpoints in `app/routers/reports.py` — not yet done, tracked in
   ROADMAP.md Phase 6).
5. **Secrets**: set `SECRET_KEY` to a strong random value via your
   platform's secret manager, never committed to the repo.

## Mobile app

Not deployable yet — the Flutter code hasn't been run through
`flutter pub get`/`flutter build` in this environment (no Flutter SDK
available here; see `mobile/README.md`). Before any release build:

```bash
cd mobile
flutter pub get
flutter analyze
flutter test
flutter build apk      # Android
flutter build ios      # iOS, requires macOS + Xcode
```

Point the app at your deployed backend by changing `kDefaultApiBaseUrl`
in `mobile/lib/main.dart` (or, for a production build, parameterize it
via `--dart-define` instead of a hardcoded constant — not yet set up).

## Web admin dashboard

Not yet built (Phase 1 scope was backend + mobile per the explicit
execution instructions in the spec). See ROADMAP.md.
