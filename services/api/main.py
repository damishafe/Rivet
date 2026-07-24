from fastapi import FastAPI

from rivet import __version__

app = FastAPI(title="Rivet", version=__version__)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
