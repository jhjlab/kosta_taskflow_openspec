def test_create_team_success(authed_client):
    client, user, _ = authed_client
    res = client.post("/teams", json={"name": "My Team"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "My Team"
    assert len(data["invite_code"]) == 9
    assert "-" in data["invite_code"]


def test_create_team_already_in_team(authed_client):
    client, _, _ = authed_client
    client.post("/teams", json={"name": "Team 1"})
    res = client.post("/teams", json={"name": "Team 2"})
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "ALREADY_IN_TEAM"


def test_join_team_success(two_clients):
    c1, u1, c2, u2 = two_clients
    r = c1.post("/teams", json={"name": "Frontiers"})
    invite_code = r.json()["invite_code"]
    res = c2.post("/teams/join", json={"invite_code": invite_code})
    assert res.status_code == 200
    assert res.json()["team"]["name"] == "Frontiers"


def test_join_team_invalid_code_format(authed_client):
    client, _, _ = authed_client
    res = client.post("/teams/join", json={"invite_code": "abcd1234"})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


def test_join_team_not_found(authed_client):
    client, _, _ = authed_client
    res = client.post("/teams/join", json={"invite_code": "XXXX-9999"})
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_join_already_in_team(two_clients):
    c1, _, c2, _ = two_clients
    r = c1.post("/teams", json={"name": "Team A"})
    code = r.json()["invite_code"]
    c2.post("/teams/join", json={"invite_code": code})
    res = c2.post("/teams/join", json={"invite_code": code})
    assert res.status_code == 409


def test_get_members(authed_client):
    client, user, _ = authed_client
    r = client.post("/teams", json={"name": "Test"})
    team_id = r.json()["id"]
    res = client.get(f"/teams/{team_id}/members")
    assert res.status_code == 200
    members = res.json()
    assert len(members) == 1
    assert members[0]["is_owner"] is True


def test_leave_team(authed_client):
    client, user, _ = authed_client
    r = client.post("/teams", json={"name": "Test"})
    team_id = r.json()["id"]
    res = client.delete(f"/teams/{team_id}/leave")
    assert res.status_code == 200
    me = client.get("/auth/me").json()
    assert me["team_id"] is None
