from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy.engine import Engine

from rivet import __version__
from rivet.storage.db import data_dir, make_engine
from services.api import assets, brand, jobs, projects


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if app.state.engine is None:
        app.state.engine = make_engine()
    if app.state.asset_root is None:
        app.state.asset_root = data_dir()
    yield


def create_app(engine: Engine | None = None, asset_root: Path | None = None) -> FastAPI:
    app = FastAPI(title="Rivet", version=__version__, lifespan=lifespan)
    app.state.engine = engine
    app.state.asset_root = asset_root
    app.include_router(assets.router)
    app.include_router(projects.router)
    app.include_router(jobs.router)
    app.include_router(brand.router)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    return app


app = create_app()
