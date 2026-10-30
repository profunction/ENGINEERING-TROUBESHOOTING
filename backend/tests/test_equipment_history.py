from tests.conftest import auth_headers, create_customer_site_equipment, signup_company


def test_equipment_history_tracks_records_and_detects_repeats(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])
    customer, site, equipment = create_customer_site_equipment(client, auth["token"])

    for desc in ["Microphone dropout", "Microphone dropout", "Firmware updated to 5.2"]:
        resp = client.post(
            f"/equipment/{equipment['id']}/maintenance-records",
            json={"description": desc},
            headers=headers,
        )
        assert resp.status_code == 201

    history = client.get(f"/equipment/{equipment['id']}/history", headers=headers).json()
    assert history["total_incidents"] == 3
    assert "microphone dropout" in history["repeated_descriptions"]
    assert "firmware updated to 5.2" not in history["repeated_descriptions"]
    assert history["equipment"]["id"] == equipment["id"]
    # No AI-generated hypothesis should be mixed into the deterministic facts.
    assert "AI" not in "".join(history["repeated_descriptions"])


def test_equipment_history_empty_when_no_records(client):
    auth = signup_company(client)
    headers = auth_headers(auth["token"])
    customer, site, equipment = create_customer_site_equipment(client, auth["token"])

    history = client.get(f"/equipment/{equipment['id']}/history", headers=headers).json()
    assert history["total_incidents"] == 0
    assert history["repeated_descriptions"] == []
