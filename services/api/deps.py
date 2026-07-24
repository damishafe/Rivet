from fastapi import Request

from rivet.storage.assets import AssetStore
from rivet.storage.events import EventStore
from rivet.storage.jobs import JobStore
from rivet.storage.plans import PlanStore
from rivet.storage.projects import ProjectStore


def get_project_store(request: Request) -> ProjectStore:
    return ProjectStore(request.app.state.engine)


def get_event_store(request: Request) -> EventStore:
    return EventStore(request.app.state.engine)


def get_asset_store(request: Request) -> AssetStore:
    return AssetStore(request.app.state.engine, request.app.state.asset_root)


def get_job_store(request: Request) -> JobStore:
    return JobStore(request.app.state.engine)


def get_plan_store(request: Request) -> PlanStore:
    return PlanStore(request.app.state.engine)
