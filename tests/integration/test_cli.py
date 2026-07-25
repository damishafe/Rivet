from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


@pytest.fixture()
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("RIVET_DATA_DIR", str(tmp_path))
    return tmp_path


def _fixture_images(tmp_path: Path) -> tuple[Path, Path]:
    product = tmp_path / "product.png"
    Image.new("RGB", (400, 500), (255, 59, 0)).save(product)
    logo = tmp_path / "logo.png"
    Image.new("RGBA", (200, 60), (250, 250, 250, 255)).save(logo)
    return product, logo


def test_create_ingest_plan_flow(workspace: Path) -> None:
    created = runner.invoke(app, ["create", "Kora Arc", "--seed", "7"])
    assert created.exit_code == 0, created.output
    project_id = created.output.strip()

    product, logo = _fixture_images(workspace)
    ingested = runner.invoke(app, ["ingest", project_id, str(product), str(logo)])
    assert ingested.exit_code == 0, ingested.output

    planned = runner.invoke(app, ["plan", project_id])
    assert planned.exit_code == 0, planned.output
    for shot_id in ("hook", "proof", "cta"):
        assert shot_id in planned.output


def test_ingest_rejects_missing_image(workspace: Path) -> None:
    created = runner.invoke(app, ["create", "Kora Arc"])
    project_id = created.output.strip()
    _, logo = _fixture_images(workspace)
    result = runner.invoke(app, ["ingest", project_id, str(workspace / "nope.png"), str(logo)])
    assert result.exit_code == 1


def test_commands_reject_unknown_project(workspace: Path) -> None:
    for args in (["plan", "missing"], ["ingest", "missing", "a.png", "b.png"]):
        assert runner.invoke(app, args).exit_code == 1


def test_export_without_pack_fails(workspace: Path) -> None:
    created = runner.invoke(app, ["create", "Kora Arc"])
    project_id = created.output.strip()
    result = runner.invoke(app, ["export", project_id, str(workspace / "out.zip")])
    assert result.exit_code == 1
    assert "no export pack" in result.output


def test_plan_requires_assets(workspace: Path) -> None:
    created = runner.invoke(app, ["create", "Kora Arc"])
    project_id = created.output.strip()
    result = runner.invoke(app, ["plan", project_id])
    assert result.exit_code == 1
    assert "ingest" in result.output
