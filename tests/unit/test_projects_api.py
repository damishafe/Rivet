from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine

from services.api.main import create_app


def make_client(engine: Engine) -> TestClient:
    return TestClient(create_app(engine))


def test_create_project_returns_201_with_body(engine: Engine) -> None:
    with make_client(engine) as client:
        response = client.post("/api/projects", json={"name": "Kora Arc Launch"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Kora Arc Launch"
    assert body["status"] == "draft"
    assert body["active_version"] == 1


def test_created_project_is_retrievable(engine: Engine) -> None:
    with make_client(engine) as client:
        created = client.post("/api/projects", json={"name": "Persist"}).json()
        fetched = client.get(f"/api/projects/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == created


def test_project_survives_app_restart(engine: Engine) -> None:
    with make_client(engine) as client:
        created = client.post("/api/projects", json={"name": "Resume"}).json()
    with make_client(engine) as fresh_client:
        fetched = fresh_client.get(f"/api/projects/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Resume"


def test_get_unknown_project_returns_404(engine: Engine) -> None:
    with make_client(engine) as client:
        assert client.get("/api/projects/nope").status_code == 404


def test_empty_name_rejected(engine: Engine) -> None:
    with make_client(engine) as client:
        assert client.post("/api/projects", json={"name": ""}).status_code == 422
