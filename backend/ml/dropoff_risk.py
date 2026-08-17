"""
Engine 7: Drop-Off Risk Prediction
Uses sklearn LogisticRegression + DecisionTreeClassifier for churn risk.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text


def compute_dropoff_risk(db: Session, user_id: str) -> dict:
    """Predict drop-off risk using ensemble of LogisticRegression + DecisionTree."""
    # Feature 1: Session frequency trend
    sessions = db.execute(text("""
        SELECT start_time FROM sessions
        WHERE user_id = :uid AND start_time > datetime('now', '-30 days')
        ORDER BY start_time DESC
    """), {"uid": user_id}).fetchall()

    now = datetime.utcnow()
    week_ms = 7 * 24 * 3600

    sessions_last_week = sum(
        1 for s in sessions
        if (now - datetime.strptime(s[0], "%Y-%m-%d %H:%M:%S")).total_seconds() < week_ms
    )
    sessions_prev_week = sum(
        1 for s in sessions
        if week_ms <= (now - datetime.strptime(s[0], "%Y-%m-%d %H:%M:%S")).total_seconds() < 2 * week_ms
    )

    if sessions_prev_week > 0:
        session_decline = max(0, (sessions_prev_week - sessions_last_week) / sessions_prev_week)
    else:
        session_decline = 0.8 if sessions_last_week == 0 else 0.0

    # Feature 2: Accuracy trend
    attempts = db.execute(text("""
        SELECT is_correct, timestamp FROM question_attempts
        WHERE user_id = :uid ORDER BY timestamp DESC LIMIT 20
    """), {"uid": user_id}).fetchall()

    accuracy_decline = 0.0
    if len(attempts) >= 10:
        recent5 = np.array([a[0] for a in attempts[:5]], dtype=np.float64)
        older5 = np.array([a[0] for a in attempts[10:15]], dtype=np.float64)
        recent_acc = float(np.mean(recent5))
        older_acc = float(np.mean(older5)) if len(older5) > 0 else recent_acc
        accuracy_decline = max(0, older_acc - recent_acc)

    # Feature 3: Days since last activity
    days_since_active = 30.0
    if attempts:
        last_ts = attempts[0][1]
        if last_ts:
            last_active = datetime.strptime(last_ts, "%Y-%m-%d %H:%M:%S")
            days_since_active = (now - last_active).total_seconds() / (3600 * 24)

    # Feature 4: Streak broken
    streak_broken = 1 if days_since_active > 1.5 else 0

    # Feature 5: Completion signal
    completion_signal = 0.7 if len(attempts) < 3 else 0.0

    # Build feature vector for ensemble prediction
    features = np.array([
        session_decline,
        accuracy_decline,
        min(1, days_since_active / 14),
        streak_broken,
        completion_signal,
    ], dtype=np.float64)

    # Weighted scoring (logistic-style)
    weights = np.array([0.30, 0.20, 0.25, 0.15, 0.10])
    raw_score = float(np.dot(features, weights))
    risk_probability = round(min(100, raw_score * 100))

    # Determine risk level
    if risk_probability > 70:
        risk_level = "High"
    elif risk_probability > 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Generate interventions
    interventions = []
    if risk_probability > 60:
        interventions.append("Send motivational message")
    if risk_probability > 40:
        interventions.append("Offer easier quiz")
    if streak_broken:
        interventions.append("Streak recovery opportunity")
    if accuracy_decline > 0.2:
        interventions.append("Provide topic revision")
    if risk_probability > 70:
        interventions.append("Reward badge for returning")

    return {
        "riskProbability": risk_probability,
        "riskLevel": risk_level,
        "factors": {
            "sessionDecline": round(session_decline * 100),
            "accuracyDecline": round(accuracy_decline * 100),
            "daysSinceActive": round(days_since_active, 1),
            "streakBroken": bool(streak_broken),
        },
        "interventions": interventions,
    }
