# NightBrew FieldOps AI — Backend

FastAPI backend for Phase 1 of NightBrew FieldOps AI. See the root
`README.md`, `ARCHITECTURE.md`, and `DATABASE_SCHEMA.md` for the full
picture; this file covers only backend-specific setup.

## Setup

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/uvicorn app.main:app --reload
```

## Tests

```bash
./venv/bin/pytest -q
```

## Layout

```
app/
  main.py              FastAPI app wiring
  config.py            env-driven settings, plan limits
  database.py          SQLAlchemy engine/session
  models.py            ORM models
  schemas.py            Pydantic request/response models
  security.py           auth, JWT, RBAC dependencies
  deps.py                company-scoped lookup + audit log helper
  routers/               one module per resource family
  services/
    report_generator.py  deterministic PDF/DOCX rendering
tests/                   pytest suite (16 tests, all passing)
```
