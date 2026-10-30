from tests.conftest import auth_headers, create_customer_site_equipment, signup_company


def test_create_work_order(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])
    customer, site, equipment = create_customer_site_equipment(client, auth["token"])

    resp = client.post(
        "/work-orders",
        json={
            "customer_id": customer["id"],
            "site_id": site["id"],
            "equipment_id": equipment["id"],
            "title": "HDMI input 2 not detected",
            "description": "Room 2 codec cannot detect HDMI input 2",
            "priority": "high",
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    wo = resp.json()
    assert wo["status"] == "open"
    assert wo["priority"] == "high"
    assert wo["company_id"] == auth["user"]["company_id"]


def test_work_order_status_transitions_and_closed_lock(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])
    customer, site, equipment = create_customer_site_equipment(client, auth["token"])

    wo = client.post(
        "/work-orders",
        json={"customer_id": customer["id"], "site_id": site["id"], "title": "Issue"},
        headers=headers,
    ).json()

    resp = client.patch(f"/work-orders/{wo['id']}", json={"status": "in_progress"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"

    resp = client.patch(f"/work-orders/{wo['id']}", json={"status": "closed"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"
    assert resp.json()["closed_at"] is not None

    resp = client.patch(f"/work-orders/{wo['id']}", json={"status": "open"}, headers=headers)
    assert resp.status_code == 400


def test_service_notes_structured_sections(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])
    customer, site, equipment = create_customer_site_equipment(client, auth["token"])

    wo = client.post(
        "/work-orders",
        json={"customer_id": customer["id"], "site_id": site["id"], "title": "Issue"},
        headers=headers,
    ).json()

    for note_type, content in [
        ("initial_condition", "Room 2 display has no signal."),
        ("investigation", "Checked HDMI cable, replaced transmitter."),
        ("outcome", "System working normally after replacement."),
    ]:
        resp = client.post(
            f"/work-orders/{wo['id']}/notes",
            json={"note_type": note_type, "content": content},
            headers=headers,
        )
        assert resp.status_code == 201

    notes = client.get(f"/work-orders/{wo['id']}/notes", headers=headers).json()
    assert len(notes) == 3
    assert {n["note_type"] for n in notes} == {"initial_condition", "investigation", "outcome"}


def test_engineer_can_create_work_order_but_viewer_cannot(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])
    customer, site, equipment = create_customer_site_equipment(client, auth["token"])

    engineer = client.post(
        "/auth/users",
        json={"email": "eng@acme.com", "password": "pw12345678", "full_name": "Eng", "role": "engineer"},
        headers=headers,
    ).json()
    viewer = client.post(
        "/auth/users",
        json={"email": "view@acme.com", "password": "pw12345678", "full_name": "View", "role": "viewer"},
        headers=headers,
    ).json()

    eng_token = client.post(
        "/auth/login", json={"email": "eng@acme.com", "password": "pw12345678"}
    ).json()["access_token"]
    viewer_token = client.post(
        "/auth/login", json={"email": "view@acme.com", "password": "pw12345678"}
    ).json()["access_token"]

    resp = client.post(
        "/work-orders",
        json={"customer_id": customer["id"], "site_id": site["id"], "title": "Engineer created"},
        headers=auth_headers(eng_token),
    )
    assert resp.status_code == 201

    resp = client.post(
        "/work-orders",
        json={"customer_id": customer["id"], "site_id": site["id"], "title": "Viewer attempt"},
        headers=auth_headers(viewer_token),
    )
    assert resp.status_code == 403
