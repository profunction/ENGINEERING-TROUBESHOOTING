import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    storage_dir = tempfile.mkdtemp()
    monkeypatch.setattr("app.config.REPORTS_DIR", os.path.join(storage_dir, "reports"))
    monkeypatch.setattr("app.services.report_generator.REPORTS_DIR", os.path.join(storage_dir, "reports"))

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def signup_company(client, company_name="Acme AV", email="owner@acme.com"):
    resp = client.post(
        "/auth/signup",
        json={
            "company_name": company_name,
            "industry": "av_vc",
            "owner_email": email,
            "owner_password": "supersecret123",
            "owner_full_name": "Owner Person",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return {"token": data["access_token"], "user": data["user"]}


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_customer_site_equipment(client, token):
    headers = auth_headers(token)
    customer = client.post(
        "/customers", json={"name": "Test Customer", "contact_email": "ops@customer.com"}, headers=headers
    ).json()
    site = client.post(
        "/sites", json={"customer_id": customer["id"], "name": "HQ Site"}, headers=headers
    ).json()
    equipment = client.post(
        "/equipment",
        json={
            "site_id": site["id"],
            "manufacturer": "Cisco",
            "model": "Codec EQ",
            "serial_number": "SN-001",
        },
        headers=headers,
    ).json()
    return customer, site, equipment
