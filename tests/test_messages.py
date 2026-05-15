import pytest


@pytest.fixture
def chat_client(authed_client):
    client, user, token = authed_client
    r = client.post("/teams", json={"name": "Chat Team"})
    team_id = r.json()["id"]
    return client, user, team_id


def test_send_message(chat_client):
    client, user, team_id = chat_client
    res = client.post(f"/teams/{team_id}/messages", json={"content": "Hello!"})
    assert res.status_code == 201
    data = res.json()
    assert data["content"] == "Hello!"
    assert data["user_email"] == user["email"]


def test_list_messages_initial(chat_client):
    client, user, team_id = chat_client
    client.post(f"/teams/{team_id}/messages", json={"content": "Msg 1"})
    client.post(f"/teams/{team_id}/messages", json={"content": "Msg 2"})
    res = client.get(f"/teams/{team_id}/messages")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_messages_empty(chat_client):
    client, user, team_id = chat_client
    res = client.get(f"/teams/{team_id}/messages")
    assert res.status_code == 200
    assert res.json() == []


def test_since_polling(chat_client):
    client, user, team_id = chat_client
    r1 = client.post(f"/teams/{team_id}/messages", json={"content": "First"})
    since = r1.json()["created_at"]
    client.post(f"/teams/{team_id}/messages", json={"content": "Second"})
    res = client.get(f"/teams/{team_id}/messages?since={since}")
    assert res.status_code == 200
    msgs = res.json()
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Second"


def test_message_too_long(chat_client):
    client, user, team_id = chat_client
    res = client.post(f"/teams/{team_id}/messages", json={"content": "a" * 1001})
    assert res.status_code == 400
    assert res.json()["error"]["code"] in ("TOO_LONG", "VALIDATION_ERROR")


def test_delete_own_message(chat_client):
    client, user, team_id = chat_client
    r = client.post(f"/teams/{team_id}/messages", json={"content": "Bye"})
    msg_id = r.json()["id"]
    res = client.delete(f"/messages/{msg_id}")
    assert res.status_code == 204


def test_delete_others_message_forbidden(two_clients):
    c1, u1, c2, u2 = two_clients
    r = c1.post("/teams", json={"name": "Team"})
    team_id = r.json()["id"]
    code = r.json()["invite_code"]
    c2.post("/teams/join", json={"invite_code": code})
    msg = c1.post(f"/teams/{team_id}/messages", json={"content": "C1 msg"})
    msg_id = msg.json()["id"]
    res = c2.delete(f"/messages/{msg_id}")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "NOT_OWNER"


def test_send_empty_message(chat_client):
    client, user, team_id = chat_client
    res = client.post(f"/teams/{team_id}/messages", json={"content": ""})
    assert res.status_code == 400


def test_non_member_cannot_send(authed_client):
    client, user, _ = authed_client
    res = client.post("/teams/9999/messages", json={"content": "hacking"})
    assert res.status_code == 403
