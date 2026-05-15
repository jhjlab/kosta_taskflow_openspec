import pytest


@pytest.fixture
def team_client(authed_client):
    client, user, token = authed_client
    r = client.post("/teams", json={"name": "Test Team"})
    team_id = r.json()["id"]
    return client, user, team_id


def test_create_task(team_client):
    client, user, team_id = team_client
    res = client.post(f"/teams/{team_id}/tasks", json={"title": "Fix bug"})
    assert res.status_code == 201
    assert res.json()["title"] == "Fix bug"
    assert res.json()["status"] == "TODO"


def test_list_tasks(team_client):
    client, user, team_id = team_client
    client.post(f"/teams/{team_id}/tasks", json={"title": "Task 1"})
    client.post(f"/teams/{team_id}/tasks", json={"title": "Task 2"})
    res = client.get(f"/teams/{team_id}/tasks")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_filter_my_tasks(team_client):
    client, user, team_id = team_client
    client.post(f"/teams/{team_id}/tasks", json={"title": "Mine", "assignee_id": user["id"]})
    client.post(f"/teams/{team_id}/tasks", json={"title": "Unassigned"})
    res = client.get(f"/teams/{team_id}/tasks?filter=me")
    assert res.status_code == 200
    assert all(t["assignee_id"] == user["id"] for t in res.json())


def test_filter_unassigned(team_client):
    client, user, team_id = team_client
    client.post(f"/teams/{team_id}/tasks", json={"title": "Mine", "assignee_id": user["id"]})
    client.post(f"/teams/{team_id}/tasks", json={"title": "Unassigned"})
    res = client.get(f"/teams/{team_id}/tasks?filter=unassigned")
    assert all(t["assignee_id"] is None for t in res.json())


def test_update_task_title(team_client):
    client, user, team_id = team_client
    r = client.post(f"/teams/{team_id}/tasks", json={"title": "Old"})
    task_id = r.json()["id"]
    res = client.put(f"/tasks/{task_id}", json={"title": "New Title"})
    assert res.status_code == 200
    assert res.json()["title"] == "New Title"


def test_patch_task_status(team_client):
    client, user, team_id = team_client
    r = client.post(f"/teams/{team_id}/tasks", json={"title": "Todo item"})
    task_id = r.json()["id"]
    res = client.patch(f"/tasks/{task_id}/status", json={"status": "DOING"})
    assert res.status_code == 200
    assert res.json()["status"] == "DOING"


def test_delete_task_by_creator(team_client):
    client, user, team_id = team_client
    r = client.post(f"/teams/{team_id}/tasks", json={"title": "To delete"})
    task_id = r.json()["id"]
    res = client.delete(f"/tasks/{task_id}")
    assert res.status_code == 204


def test_delete_task_forbidden(two_clients):
    c1, u1, c2, u2 = two_clients
    r = c1.post("/teams", json={"name": "Team"})
    team_id = r.json()["id"]
    code = r.json()["invite_code"]
    c2.post("/teams/join", json={"invite_code": code})
    task_r = c1.post(f"/teams/{team_id}/tasks", json={"title": "C1 task"})
    task_id = task_r.json()["id"]
    res = c2.delete(f"/tasks/{task_id}")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


def test_invalid_status(team_client):
    client, user, team_id = team_client
    r = client.post(f"/teams/{team_id}/tasks", json={"title": "item"})
    task_id = r.json()["id"]
    res = client.patch(f"/tasks/{task_id}/status", json={"status": "INVALID"})
    assert res.status_code == 400
