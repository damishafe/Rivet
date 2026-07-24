import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from sse_starlette import EventSourceResponse, ServerSentEvent

from rivet.storage.events import EventStore

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _resume_cursor(after: int, header: str | None) -> int:
    if header is None:
        return after
    try:
        return max(after, int(header))
    except ValueError:
        return after


@router.get("/{job_id}/events")
async def stream_events(
    job_id: str, request: Request, after: int = 0, follow: bool = True
) -> EventSourceResponse:
    store = EventStore(request.app.state.engine)
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
