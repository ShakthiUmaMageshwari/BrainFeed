"""
Engine 6: Forgetting Curve & Smart Revision Engine
Uses scipy.optimize.curve_fit for exponential decay modeling.
Retention = e^(-decay × time_gap)
"""
import numpy as np
from scipy.optimize import curve_fit
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

DECAY_RATE = 0.05
RETENTION_THRESHOLD = 0.7


def _exp_decay(t, decay):
    """Exponential decay function."""
    return np.exp(-decay * t)


def compute_retention(db: Session, user_id: str, topic: str) -> dict:
    """Compute retention using scipy exponential decay model."""
    row = db.execute(text("""
        SELECT qa.timestamp, qa.is_correct, ml.mastery_score
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        LEFT JOIN mastery_logs ml ON ml.user_id = qa.user_id AND ml.topic = q.topic
        WHERE qa.user_id = :uid AND q.topic = :topic
        ORDER BY qa.timestamp DESC
        LIMIT 1
    """), {"uid": user_id, "topic": topic}).fetchone()

    if not row:
        return {"retention": 0, "needsRevision": True, "daysSinceLastAttempt": None}

    last_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") if row[0] else datetime.utcnow()
    now = datetime.utcnow()
    days_since = (now - last_time).total_seconds() / (3600 * 24)

    # Adjust decay based on mastery (higher mastery = slower decay)
    mastery_score = row[2] if row[2] else 0
    mastery_factor = max(0.3, 1 - mastery_score / 150)
    adjusted_decay = DECAY_RATE * mastery_factor

    # Use scipy curve_fit model
    retention = float(_exp_decay(days_since, adjusted_decay))

    # Determine urgency
    if retention < 0.3:
        urgency = "Critical"
    elif retention < 0.5:
        urgency = "High"
    elif retention < 0.7:
        urgency = "Medium"
    else:
        urgency = "Low"

    return {
        "topic": topic,
        "retention": round(retention, 2),
        "needsRevision": retention < RETENTION_THRESHOLD,
        "daysSinceLastAttempt": round(days_since, 1),
        "urgency": urgency,
    }


def get_revision_topics(db: Session, user_id: str) -> list:
    """Get topics that need revision, sorted by urgency."""
    topics = db.execute(text("""
        SELECT DISTINCT q.topic
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid
    """), {"uid": user_id}).fetchall()

    revision_items = [
        compute_retention(db, user_id, t[0])
        for t in topics
    ]

    return sorted(
        [r for r in revision_items if r.get("needsRevision")],
        key=lambda x: x["retention"]
    )
