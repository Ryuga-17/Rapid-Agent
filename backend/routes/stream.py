import asyncio
import json
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from backend.events import event_bus
from backend.services.mongodb_service import MongoDBService

router = APIRouter()
db_service = MongoDBService()

@router.get("/stream/events/{trace_id}")
async def stream_events(request: Request, trace_id: str):
    """
    Subscribes to execution events for a specific trace_id and streams them via SSE.
    """
    queue = event_bus.subscribe(trace_id)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                # Wait for the next event in the queue
                event = await queue.get()
                yield {
                    "event": event["event_type"],
                    "data": json.dumps(event)
                }
        finally:
            event_bus.unsubscribe(trace_id, queue)

    return EventSourceResponse(event_generator())

@router.get("/traces")
async def get_traces():
    """
    Retrieves the history of all execution traces for Replay Mode.
    """
    traces = db_service.get_execution_traces()
    # Serialize ObjectId to string
    for t in traces:
        if "_id" in t:
            t["_id"] = str(t["_id"])
    return traces
