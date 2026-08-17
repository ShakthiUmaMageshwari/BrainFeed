"""
Engine 1: Dynamic Knowledge Mastery Model
Uses NumPy vectorized operations for weighted mastery computation.
Mastery = (Accuracy × 0.4) + (DifficultyFactor × 0.3) + (Consistency × 0.2) + (SpeedEfficiency × 0.1)
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.ml.bkt import calculate_topic_mastery_bkt


def compute_mastery(db: Session, user_id: str, topic: str) -> dict:
    """Compute per-topic mastery score using Bayesian Knowledge Tracing (BKT)."""
    rows = db.execute(text("""
        SELECT qa.is_correct
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid AND q.topic = :topic
        ORDER BY qa.timestamp ASC
    """), {"uid": user_id, "topic": topic}).fetchall()

    if not rows:
        return {"score": 0, "level": "Novice"}

    # BKT calculation
    history = [bool(r[0]) for r in rows]
    probability_known = calculate_topic_mastery_bkt(history)
    
    # Scale to 0-100
    mastery_score = int(probability_known * 100)
    level = _get_level(mastery_score)

    return {"score": mastery_score, "level": level}

    return {"score": mastery_score, "level": level}


def _get_level(score: int) -> str:
    if score >= 85:
        return "Advanced"
    if score >= 65:
        return "Competent"
    if score >= 40:
        return "Developing"
    return "At Risk"


def update_mastery_in_db(db: Session, user_id: str, topic: str) -> dict:
    """Compute mastery and upsert into mastery_logs."""
    result = compute_mastery(db, user_id, topic)
    score, level = result["score"], result["level"]

    db.execute(text("""
        INSERT INTO mastery_logs (user_id, topic, mastery_score, level, updated_at)
        VALUES (:uid, :topic, :score, :level, datetime('now'))
        ON CONFLICT(user_id, topic) DO UPDATE SET
            mastery_score = :score,
            level = :level,
            updated_at = datetime('now')
    """), {"uid": user_id, "topic": topic, "score": score, "level": level})
    db.commit()

    return {"topic": topic, "score": score, "level": level}


def get_all_mastery(db: Session, user_id: str) -> list:
    """Compute mastery for all topics the user has attempted."""
    topics = db.execute(text("""
        SELECT DISTINCT q.topic
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid
    """), {"uid": user_id}).fetchall()

    return [
        {"topic": t[0], **compute_mastery(db, user_id, t[0])}
        for t in topics
    ]
