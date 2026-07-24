from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.engine import Engine

from rivet import __version__
from rivet.storage.db import make_engine
from services.api import projects


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if app.state.engine is None:
        app.state.engine = make_engine()
    yield


def create_app(engine: Engine | None = None) -> FastAPI:
    app = FastAPI(title="Rivet", version=__version__, lifespan=lifespan)
    app.state.engine = engine
    app.include_router(projects.router)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    return app


app = create_app()
