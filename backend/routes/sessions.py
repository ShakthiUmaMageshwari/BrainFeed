"""
Session routes: Start and End sessions
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.db.database import get_db
from backend.db.models import SessionModel

router = APIRouter()


class StartSessionRequest(BaseModel):
    userId: str
    deviceType: Optional[str] = "web"


class EndSessionRequest(BaseModel):
    sessionId: str


@router.post("/start")
def start_session(req: StartSessionRequest, db: Session = Depends(get_db)):
    try:
        if not req.userId:
            raise HTTPException(status_code=400, detail="userId is required.")

        session_id = str(uuid.uuid4())
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        session = SessionModel(
            id=session_id,
            user_id=req.userId,
            device_type=req.deviceType or "web",
            start_time=now,
        )
        db.add(session)
        db.commit()

        return {"success": True, "sessionId": session_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Sessions] Start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start session.")


@router.post("/end")
def end_session(req: EndSessionRequest, db: Session = Depends(get_db)):
    try:
        if not req.sessionId:
            raise HTTPException(status_code=400, detail="sessionId is required.")

        session = db.query(SessionModel).filter(SessionModel.id == req.sessionId).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")

        start_time = datetime.strptime(session.start_time, "%Y-%m-%d %H:%M:%S")
        duration = (datetime.utcnow() - start_time).total_seconds()

        session.end_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        session.session_duration_seconds = duration
        db.commit()

        return {
            "success": True,
            "duration": round(duration),
            "questionsAttempted": session.questions_attempted,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Sessions] End error: {e}")
        raise HTTPException(status_code=500, detail="Failed to end session.")
