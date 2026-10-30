from tests.conftest import auth_headers, create_customer_site_equipment, signup_company


def test_company_b_cannot_see_company_a_customers(client):
    auth_a = signup_company(client, "Company A", "owner-a@test.com")
    auth_b = signup_company(client, "Company B", "owner-b@test.com")

    customer_a, site_a, equipment_a = create_customer_site_equipment(client, auth_a["token"])

    resp = client.get(f"/customers/{customer_a['id']}", headers=auth_headers(auth_b["token"]))
    assert resp.status_code == 404

    resp = client.get("/customers", headers=auth_headers(auth_b["token"]))
    assert resp.json() == []

    resp = client.get("/customers", headers=auth_headers(auth_a["token"]))
    assert len(resp.json()) == 1


def test_company_b_cannot_create_work_order_against_company_a_site(client):
    auth_a = signup_company(client, "Company A", "owner-a2@test.com")
    auth_b = signup_company(client, "Company B", "owner-b2@test.com")

    customer_a, site_a, equipment_a = create_customer_site_equipment(client, auth_a["token"])

    resp = client.post(
        "/work-orders",
        json={"customer_id": customer_a["id"], "site_id": site_a["id"], "title": "Cross-tenant attempt"},
        headers=auth_headers(auth_b["token"]),
    )
    assert resp.status_code == 404


def test_company_b_cannot_view_company_a_equipment_history(client):
    auth_a = signup_company(client, "Company A", "owner-a3@test.com")
    auth_b = signup_company(client, "Company B", "owner-b3@test.com")

    customer_a, site_a, equipment_a = create_customer_site_equipment(client, auth_a["token"])

    resp = client.get(f"/equipment/{equipment_a['id']}/history", headers=auth_headers(auth_b["token"]))
    assert resp.status_code == 404
