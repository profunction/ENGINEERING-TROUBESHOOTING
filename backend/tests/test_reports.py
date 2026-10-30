import os

from tests.conftest import auth_headers, create_customer_site_equipment, signup_company


def test_generate_report_creates_pdf_and_docx(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])
    customer, site, equipment = create_customer_site_equipment(client, auth["token"])

    wo = client.post(
        "/work-orders",
        json={"customer_id": customer["id"], "site_id": site["id"], "equipment_id": equipment["id"], "title": "Issue"},
        headers=headers,
    ).json()

    resp = client.post(
        f"/work-orders/{wo['id']}/report",
        json={
            "initial_condition": "No HDMI signal on input 2.",
            "investigation": "Swapped HDMI cable; fault followed the cable.",
            "outcome": "Replaced faulty HDMI cable; input restored.",
            "follow_up": "None.",
            "engineer_signature_name": "Owner Person",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    report = resp.json()
    assert os.path.exists(report["pdf_path"])
    assert os.path.exists(report["docx_path"])

    pdf_resp = client.get(f"/work-orders/{wo['id']}/report/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"


def test_report_marks_missing_fields_for_confirmation_not_fabricated(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])
    customer, site, equipment = create_customer_site_equipment(client, auth["token"])

    wo = client.post(
        "/work-orders",
        json={"customer_id": customer["id"], "site_id": site["id"], "title": "Issue"},
        headers=headers,
    ).json()

    resp = client.post(
        f"/work-orders/{wo['id']}/report",
        json={"initial_condition": "Reported: no display."},
        headers=headers,
    )
    assert resp.status_code == 201
    report = resp.json()
    assert report["outcome"] is None

    with open(report["docx_path"], "rb") as f:
        pass  # existence already proven; content assertions covered by generator unit test below

    from docx import Document

    doc = Document(report["docx_path"])
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "REQUIRES ENGINEER CONFIRMATION" in text
    assert "customer signed off" not in text.lower()
