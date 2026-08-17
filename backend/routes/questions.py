"""
Questions routes: Feed and Submit
Integrates adaptive difficulty, recommendations, cognitive load, mastery, auto difficulty.
"""
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional

from backend.db.database import get_db, SessionLocal
from backend.utils.cache import cache
from backend.ml.adaptive_difficulty import get_adaptive_difficulty
from backend.ml.recommendation_engine import get_recommended_questions
from backend.ml.cognitive_load import analyze_cognitive_load
from backend.ml.mastery_model import update_mastery_in_db
from backend.ml.auto_difficulty import update_question_stats

router = APIRouter()

def background_ml_update(user_id: str, topic: str, question_id: str):
    """Run heavy ML updates in background and invalidate cache."""
    db = SessionLocal()
    try:
        # 1. Update Mastery
        update_mastery_in_db(db, user_id, topic)
        
        # 2. Update Question Stats (IRT/Difficulty)
        update_question_stats(db, question_id)
        
        db.commit()
        
        # 3. Invalidate Cache
        cache.delete(f"mastery:{user_id}")
        cache.delete(f"prediction:{user_id}")
        cache.delete(f"readiness:{user_id}")
        
    except Exception as e:
        print(f"❌ [Background ML] Error: {e}")
    finally:
        db.close()

class SubmitAnswerRequest(BaseModel):
    userId: str
    questionId: str
    selectedOption: str
    responseTime: Optional[float] = 0
    responseTimeSeconds: Optional[float] = 0
    sessionId: Optional[str] = None
    hintUsed: Optional[bool] = False
    explanationOpened: Optional[bool] = False

    @property
    def actual_response_time(self) -> float:
        """Frontend sends 'responseTime', handle both field names."""
        return self.responseTime or self.responseTimeSeconds or 0


@router.get("/feed")
def get_feed(
    userId: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sessionId: Optional[str] = Query(None),
    limit: Optional[int] = Query(5),
    db: DBSession = Depends(get_db),
):
    try:
        if not userId:
            # Unauthenticated: return random questions
            rows = db.execute(text("""
                SELECT * FROM questions ORDER BY RANDOM() LIMIT :lim
            """), {"lim": limit}).fetchall()
            return {
                "questions": [_row_to_question(r) for r in rows],
                "total": len(rows),
                "adaptiveDifficulty": None,
                "cognitiveLoad": None,
            }

        # Authenticated: adaptive difficulty + recommendations
        adaptive = get_adaptive_difficulty(db, userId)
        difficulty = adaptive["selectedDifficulty"]

        # Get recommended questions (topic-aware)
        recommended = get_recommended_questions(db, userId, category, limit)

        if not recommended:
            # Fallback: random questions at chosen difficulty
            rows = db.execute(text("""
                SELECT * FROM questions
                WHERE difficulty = :diff
                ORDER BY RANDOM()
                LIMIT :lim
            """), {"diff": difficulty, "lim": limit}).fetchall()
            recommended = [_row_to_question(r) for r in rows]

        # Cognitive load analysis
        cognitive_load = analyze_cognitive_load(db, userId, sessionId) if sessionId else None

        return {
            "questions": recommended,
            "total": len(recommended),
            "adaptiveDifficulty": adaptive,
            "cognitiveLoad": cognitive_load,
        }
    except Exception as e:
        print(f"[Questions] Feed error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feed.")


@router.post("/submit")
def submit_answer(
    req: SubmitAnswerRequest, 
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db)
):
    try:
        # Get the question
        question_row = db.execute(text("""
            SELECT * FROM questions WHERE id = :qid
        """), {"qid": req.questionId}).fetchone()

        if not question_row:
            raise HTTPException(status_code=404, detail="Question not found.")

        q = _row_to_question(question_row)
        is_correct = 1 if req.selectedOption == q["correct_answer"] else 0

        # Get attempt number
        prev = db.execute(text("""
            SELECT COUNT(*) FROM question_attempts
            WHERE user_id = :uid AND question_id = :qid
        """), {"uid": req.userId, "qid": req.questionId}).fetchone()
        attempt_number = (prev[0] or 0) + 1

        # Record attempt
        attempt_id = str(uuid.uuid4())
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        db.execute(text("""
            INSERT INTO question_attempts
            (id, user_id, question_id, session_id, selected_option, is_correct,
             response_time_seconds, hint_used, explanation_opened, attempt_number, timestamp)
            VALUES (:id, :uid, :qid, :sid, :opt, :correct, :time, :hint, :expl, :attempt, :ts)
        """), {
            "id": attempt_id,
            "uid": req.userId,
            "qid": req.questionId,
            "sid": req.sessionId,
            "opt": req.selectedOption,
            "correct": is_correct,
            "time": req.actual_response_time,
            "hint": 1 if req.hintUsed else 0,
            "expl": 1 if req.explanationOpened else 0,
            "attempt": attempt_number,
            "ts": now,
        })

        # Update session questions attempted count
        if req.sessionId:
            db.execute(text("""
                UPDATE sessions
                SET questions_attempted = questions_attempted + 1
                WHERE id = :sid
            """), {"sid": req.sessionId})

        db.commit()

        # Schedule ML updates in background
        background_tasks.add_task(background_ml_update, req.userId, q.get("topic", ""), req.questionId)

        # Calculate current streak
        recent = db.execute(text("""
            SELECT is_correct FROM question_attempts
            WHERE user_id = :uid ORDER BY timestamp DESC LIMIT 20
        """), {"uid": req.userId}).fetchall()
        streak = 0
        for r in recent:
            if r[0]:
                streak += 1
            else:
                break

        return {
            "success": True,
            "isCorrect": bool(is_correct),
            "correctAnswer": q["correct_answer"],
            "explanation": q.get("explanation", ""),
            "streak": streak,
            "mastery": None, # Frontend should fetch fresh mastery from dashboard if needed, or we accept it's slightly stale here
            "attemptNumber": attempt_number,
            "message": "Answer recorded. AI analysis running in background."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Questions] Submit error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit answer.")


def _row_to_question(row) -> dict:
    """Convert a raw DB row to a question dict."""
    if hasattr(row, "_mapping"):
        d = dict(row._mapping)
    else:
        keys = ["id", "subject", "topic", "subtopic", "exam_tag", "difficulty",
                "question_text", "options", "correct_answer", "explanation", "created_at"]
        d = dict(zip(keys, row))

    if isinstance(d.get("options"), str):
        try:
            d["options"] = json.loads(d["options"])
        except (json.JSONDecodeError, TypeError):
            pass
    return d
