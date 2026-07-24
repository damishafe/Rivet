from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine

from rivet import __version__
from services.api.main import create_app


def test_version_is_set() -> None:
    assert __version__


def test_health_endpoint(engine: Engine) -> None:
    with TestClient(create_app(engine)) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
