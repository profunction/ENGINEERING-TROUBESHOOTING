from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, companies, customers, equipment, reports, work_orders

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NightBrew FieldOps AI",
    description="AI Field Service Engineer Copilot + Field Service Management API (Phase 1 MVP)",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(customers.router)
app.include_router(equipment.router)
app.include_router(work_orders.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}
