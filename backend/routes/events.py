from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from datetime import datetime

from backend.db.database import get_db, SessionLocal
from backend.db.models import EventLog

router = APIRouter()

class EventLogRequest(BaseModel):
    userId: str
    eventType: str
    eventData: Optional[Dict[str, Any]] = {}
    timestamp: Optional[str] = None

def _log_event_background(data: EventLogRequest):
    """Write event to DB in background."""
    db = SessionLocal()
    try:
        new_event = EventLog(
            user_id=data.userId,
            event_type=data.eventType,
            event_data=json.dumps(data.eventData) if data.eventData else "{}",
            timestamp=data.timestamp or datetime.utcnow().isoformat()
        )
        db.add(new_event)
        db.commit()
    except Exception as e:
        print(f"❌ [EventLog] Error writing log: {e}")
    finally:
        db.close()

@router.post("/")
def log_event(req: EventLogRequest, background_tasks: BackgroundTasks):
    """
    Ingest behavioral events (Scroll, Hover, Drop-off, etc.)
    Fire-and-forget logging via background task.
    """
    try:
        background_tasks.add_task(_log_event_background, req)
        return {"status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
