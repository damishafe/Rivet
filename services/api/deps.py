from fastapi import Request

from rivet.storage.projects import ProjectStore


def get_project_store(request: Request) -> ProjectStore:
    return ProjectStore(request.app.state.engine)
