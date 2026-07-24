from fastapi.testclient import TestClient

from rivet import __version__
from services.api.main import app


def test_version_is_set() -> None:
    assert __version__


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
