import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.database import Base
from backend.dependencies import get_db

SQLALCHEMY_TEST_URL = "sqlite://"


@pytest.fixture
def db():
    engine = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def authed_client(client):
    res = client.post("/auth/signup", json={"email": "test@example.com", "password": "password123"})
    token = res.json()["token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    user = res.json()["user"]
    return client, user, token


@pytest.fixture
def two_clients(db):
    """두 명의 인증된 클라이언트 반환 (팀 테스트용)"""
    app.dependency_overrides[get_db] = lambda: db
    c1 = TestClient(app)
    c2 = TestClient(app)
    r1 = c1.post("/auth/signup", json={"email": "user1@example.com", "password": "password123"})
    r2 = c2.post("/auth/signup", json={"email": "user2@example.com", "password": "password123"})
    c1.headers.update({"Authorization": f"Bearer {r1.json()['token']}"})
    c2.headers.update({"Authorization": f"Bearer {r2.json()['token']}"})
    yield c1, r1.json()["user"], c2, r2.json()["user"]
    app.dependency_overrides.clear()
