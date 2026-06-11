import asyncio
import json
import time
from typing import Any, Dict, Optional
from datetime import datetime, timezone
import contextvars
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Context variable to hold the trace_id for the current request
current_trace_id = contextvars.ContextVar("current_trace_id", default=None)
# Context variable to hold the trace payload for the current request (for replay saving)
current_trace_data = contextvars.ContextVar("current_trace_data", default=None)

from fastapi.encoders import jsonable_encoder

class EventEmitter:
    def __init__(self):
        # Dictionary mapping trace_id to a list of asyncio.Queues (one queue per subscriber)
        self._subscribers: Dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, trace_id: str) -> asyncio.Queue:
        """Subscribe to events for a specific trace_id."""
        if trace_id not in self._subscribers:
            self._subscribers[trace_id] = []
        queue = asyncio.Queue()
        self._subscribers[trace_id].append(queue)
        return queue

    def unsubscribe(self, trace_id: str, queue: asyncio.Queue):
        """Remove a subscriber."""
        if trace_id in self._subscribers:
            try:
                self._subscribers[trace_id].remove(queue)
                if not self._subscribers[trace_id]:
                    del self._subscribers[trace_id]
            except ValueError:
                pass

    def emit(self, trace_id: str, event_type: str, payload: Dict[str, Any]):
        """Emit an event to all subscribers of a trace_id."""
        if not trace_id:
            return

        event_data = {
            "trace_id": trace_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload
        }
        
        # Save to local context trace data for DB persistence
        trace_data = current_trace_data.get()
        if trace_data is not None:
            trace_data.append(event_data)

        if trace_id in self._subscribers:
            for queue in self._subscribers[trace_id]:
                try:
                    queue.put_nowait(event_data)
                except asyncio.QueueFull:
                    logger.error("Event queue full, dropping event.")

# Global event emitter instance
event_bus = EventEmitter()

def track_execution(stage_name: str):
    """
    Decorator to wrap functions and emit STARTED, COMPLETED, and FAILED events.
    Automatically captures the function's output and pushes it to the payload.
    Works for both sync and async functions.
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                trace_id = current_trace_id.get()
                if trace_id:
                    event_bus.emit(trace_id, "STAGE_STARTED", {"stage": stage_name})
                
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    if trace_id:
                        # Convert models to dict if they have model_dump/dict methods
                        res_data = jsonable_encoder(result)
                        
                        event_bus.emit(trace_id, "STAGE_COMPLETED", {
                            "stage": stage_name,
                            "duration_sec": round(duration, 3),
                            "result": res_data
                        })
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    if trace_id:
                        event_bus.emit(trace_id, "STAGE_FAILED", {
                            "stage": stage_name,
                            "duration_sec": round(duration, 3),
                            "error": str(e)
                        })
                    raise e
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                trace_id = current_trace_id.get()
                if trace_id:
                    event_bus.emit(trace_id, "STAGE_STARTED", {"stage": stage_name})
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    if trace_id:
                        res_data = jsonable_encoder(result)

                        event_bus.emit(trace_id, "STAGE_COMPLETED", {
                            "stage": stage_name,
                            "duration_sec": round(duration, 3),
                            "result": res_data
                        })
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    if trace_id:
                        event_bus.emit(trace_id, "STAGE_FAILED", {
                            "stage": stage_name,
                            "duration_sec": round(duration, 3),
                            "error": str(e)
                        })
                    raise e
            return sync_wrapper
    return decorator
