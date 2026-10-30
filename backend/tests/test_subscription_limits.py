from tests.conftest import auth_headers, signup_company


def test_starter_plan_has_finite_ai_quota_and_usage_endpoint(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])

    resp = client.get("/companies/me/usage", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["plan"] == "starter"
    assert data["ai_requests_limit"] == 200
    assert data["ai_requests_used_this_month"] == 0
    assert data["ai_requests_remaining"] == 200
    assert data["over_limit"] is False


def test_usage_endpoint_requires_supervisor_role(client):
    from tests.test_permissions import make_user

    auth = signup_company(client)
    owner_headers = auth_headers(auth["token"])
    engineer_token = make_user(client, owner_headers, "eng-usage@test.com", "engineer")

    resp = client.get("/companies/me/usage", headers=auth_headers(engineer_token))
    assert resp.status_code == 403
