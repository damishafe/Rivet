import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette import EventSourceResponse, ServerSentEvent

from rivet.domain.jobs import Job
from rivet.storage.events import EventStore
from rivet.storage.jobs import JobStore
from services.api.deps import get_event_store, get_job_store

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _resume_cursor(after: int, header: str | None) -> int:
    if header is None:
        return after
    try:
        return max(after, int(header))
    except ValueError:
        return after


@router.get("/{job_id}")
def get_job(job_id: str, store: JobStore = Depends(get_job_store)) -> Job:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@router.post("/{job_id}/cancel", status_code=202)
def cancel_job(job_id: str, store: JobStore = Depends(get_job_store)) -> Job:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    store.request_cancel(job_id)
    return job


@router.get("/{job_id}/events")
async def stream_events(
    job_id: str, request: Request, after: int = 0, follow: bool = True,
    store: EventStore = Depends(get_event_store)
) -> EventSourceResponse:
    cursor_start = _resume_cursor(after, request.headers.get("last-event-id"))

    async def generate() -> AsyncIterator[ServerSentEvent]:
        cursor = cursor_start
        while True:
            for seq, event in store.list_after(job_id, cursor):
                cursor = seq
                yield ServerSentEvent(
                    data=event.model_dump_json(), id=str(seq), event="stage"
                )
            if not follow or await request.is_disconnected():
                return
            await asyncio.sleep(0.5)

    return EventSourceResponse(generate())
