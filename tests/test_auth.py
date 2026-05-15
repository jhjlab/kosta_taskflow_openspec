def test_signup_success(client):
    res = client.post("/auth/signup", json={"email": "new@example.com", "password": "password123"})
    assert res.status_code == 201
    data = res.json()
    assert "token" in data
    assert data["user"]["email"] == "new@example.com"
    assert data["user"]["team_id"] is None


def test_signup_duplicate_email(client):
    client.post("/auth/signup", json={"email": "dup@example.com", "password": "password123"})
    res = client.post("/auth/signup", json={"email": "dup@example.com", "password": "password123"})
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "EMAIL_TAKEN"


def test_signup_short_password(client):
    res = client.post("/auth/signup", json={"email": "user@example.com", "password": "short"})
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_success(client):
    client.post("/auth/signup", json={"email": "user@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "token" in res.json()


def test_login_wrong_password(client):
    client.post("/auth/signup", json={"email": "user@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "user@example.com", "password": "wrongpassword"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_nonexistent_email(client):
    res = client.post("/auth/login", json={"email": "notexist@example.com", "password": "password123"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_success(authed_client):
    client, user, _ = authed_client
    res = client.get("/auth/me")
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"


def test_me_no_token(client):
    res = client.get("/auth/me")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "TOKEN_EXPIRED"


def test_logout(authed_client):
    client, _, _ = authed_client
    res = client.post("/auth/logout")
    assert res.status_code == 200
