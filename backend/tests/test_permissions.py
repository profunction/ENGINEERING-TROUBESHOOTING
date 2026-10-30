from tests.conftest import auth_headers, signup_company


def make_user(client, owner_headers, email, role):
    client.post(
        "/auth/users",
        json={"email": email, "password": "pw12345678", "full_name": role.title(), "role": role},
        headers=owner_headers,
    )
    return client.post("/auth/login", json={"email": email, "password": "pw12345678"}).json()["access_token"]


def test_only_admin_or_owner_can_create_users(client):
    auth = signup_company(client)
    owner_headers = auth_headers(auth["token"])
    engineer_token = make_user(client, owner_headers, "eng-perm@test.com", "engineer")

    resp = client.post(
        "/auth/users",
        json={"email": "nope@test.com", "password": "pw12345678", "full_name": "Nope", "role": "viewer"},
        headers=auth_headers(engineer_token),
    )
    assert resp.status_code == 403


def test_only_supervisor_and_above_can_create_customers(client):
    auth = signup_company(client)
    owner_headers = auth_headers(auth["token"])
    viewer_token = make_user(client, owner_headers, "viewer-perm@test.com", "viewer")
    supervisor_token = make_user(client, owner_headers, "sup-perm@test.com", "supervisor")

    resp = client.post("/customers", json={"name": "X"}, headers=auth_headers(viewer_token))
    assert resp.status_code == 403

    resp = client.post("/customers", json={"name": "X"}, headers=auth_headers(supervisor_token))
    assert resp.status_code == 201


def test_only_supervisor_and_above_can_list_users(client):
    auth = signup_company(client)
    owner_headers = auth_headers(auth["token"])
    engineer_token = make_user(client, owner_headers, "eng-list@test.com", "engineer")

    resp = client.get("/auth/users", headers=auth_headers(engineer_token))
    assert resp.status_code == 403

    resp = client.get("/auth/users", headers=owner_headers)
    assert resp.status_code == 200
