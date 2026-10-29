import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app, get_db


@pytest.fixture
def client():
    # Create a separate temporary in-memory database for this test.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_project(client):
    response = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "description": "Created by an automated test",
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Test Project"
    assert response.json()["description"] == "Created by an automated test"
    assert isinstance(response.json()["id"], int)


def test_list_projects(client):
    client.post(
        "/projects",
        json={"name": "Listed Project", "description": "Test description"},
    )

    response = client.get("/projects")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Listed Project"


def test_get_missing_project(client):
    response = client.get("/projects/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


def test_create_project_rejects_empty_name(client):
    response = client.post(
        "/projects",
        json={"name": "", "description": "Invalid project"},
    )

    assert response.status_code == 422


def test_create_project_rejects_long_name(client):
    response = client.post(
        "/projects",
        json={"name": "A" * 101, "description": ""},
    )

    assert response.status_code == 422
