"""
Engine 8: Auto Difficulty Calibration
Uses global stats to auto-adjust question difficulty tags.
<25% success → Hard, 25-70% → Medium, >70% → Easy
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text


def update_question_stats(db: Session, question_id: str) -> dict:
    """Update global question stats and compute difficulty."""
    row = db.execute(text("""
        SELECT COUNT(*) as total, SUM(is_correct) as correct,
               AVG(response_time_seconds) as avg_time
        FROM question_attempts
        WHERE question_id = :qid
    """), {"qid": question_id}).fetchone()

    if not row or row[0] == 0:
        return None

    total, correct, avg_time = row[0], row[1] or 0, row[2] or 0
    success_rate = correct / total

    if success_rate < 0.25:
        computed_difficulty = "Hard"
    elif success_rate < 0.70:
        computed_difficulty = "Medium"
    else:
        computed_difficulty = "Easy"

    db.execute(text("""
        INSERT INTO question_stats (question_id, total_attempts, total_correct, avg_response_time, computed_difficulty, updated_at)
        VALUES (:qid, :total, :correct, :avg_time, :diff, datetime('now'))
        ON CONFLICT(question_id) DO UPDATE SET
            total_attempts = :total,
            total_correct = :correct,
            avg_response_time = :avg_time,
            computed_difficulty = :diff,
            updated_at = datetime('now')
    """), {
        "qid": question_id,
        "total": total,
        "correct": correct,
        "avg_time": avg_time,
        "diff": computed_difficulty,
    })
    db.commit()

    return {
        "questionId": question_id,
        "totalAttempts": total,
        "successRate": round(success_rate * 100),
        "avgResponseTime": round(avg_time, 1),
        "originalDifficulty": None,
        "computedDifficulty": computed_difficulty,
    }
