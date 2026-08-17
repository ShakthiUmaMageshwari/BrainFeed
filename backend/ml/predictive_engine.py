"""
Engine 2: Predictive Performance Engine
Uses sklearn LinearRegression + Ridge + Lasso to predict next quiz score
and estimate exam readiness date.
"""
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sqlalchemy.orm import Session
from sqlalchemy import text


def predict_next_score(db: Session, user_id: str) -> dict:
    """Predict next quiz score using sklearn regression models."""
    rows = db.execute(text("""
        SELECT is_correct, timestamp
        FROM question_attempts
        WHERE user_id = :uid
        ORDER BY timestamp DESC
        LIMIT 50
    """), {"uid": user_id}).fetchall()

    if len(rows) < 3:
        return {"predictedScore": None, "weeklyImprovement": None, "message": "Not enough data for prediction"}

    # Group into windows of 5 and compute accuracy for each window
    correct = [r[0] for r in rows]
    windows = []
    window_size = 5
    for i in range(0, len(correct), window_size):
        w = correct[i:i + window_size]
        if len(w) >= 3:
            windows.append(sum(w) / len(w) * 100)

    windows.reverse()  # chronological order

    if len(windows) < 2:
        return {"predictedScore": None, "weeklyImprovement": None, "message": "Not enough data for prediction"}

    # Build regression features
    X = np.arange(len(windows)).reshape(-1, 1)
    y = np.array(windows)

    # Fit multiple models and ensemble
    lr = LinearRegression()
    ridge = Ridge(alpha=1.0)
    lasso = Lasso(alpha=0.1)

    lr.fit(X, y)
    ridge.fit(X, y)
    lasso.fit(X, y)

    # Predict next window (ensemble: average of 3 models)
    next_x = np.array([[len(windows)]])
    pred_lr = lr.predict(next_x)[0]
    pred_ridge = ridge.predict(next_x)[0]
    pred_lasso = lasso.predict(next_x)[0]

    predicted_score = int(np.clip(np.mean([pred_lr, pred_ridge, pred_lasso]), 0, 100))

    # Weekly improvement (slope from LinearRegression)
    slope = float(lr.coef_[0])
    weekly_improvement = round(slope, 2)

    # Trend classification
    if slope > 0.5:
        trend = "Improving"
    elif slope < -0.5:
        trend = "Declining"
    else:
        trend = "Stable"

    confidence = "High" if len(windows) >= 5 else "Medium" if len(windows) >= 3 else "Low"

    return {
        "predictedScore": predicted_score,
        "weeklyImprovement": weekly_improvement,
        "trend": trend,
        "confidence": confidence,
    }


def estimate_readiness_date(db: Session, user_id: str, target_exam: str) -> dict:
    """Estimate weeks to reach 80% readiness using regression trajectory."""
    rows = db.execute(text("""
        SELECT mastery_score FROM mastery_logs WHERE user_id = :uid
    """), {"uid": user_id}).fetchall()

    if not rows:
        return {"readinessPercentage": 0, "estimatedWeeks": None}

    mastery_scores = np.array([r[0] for r in rows], dtype=np.float64)
    avg_mastery = float(np.mean(mastery_scores))
    readiness_pct = round(avg_mastery)

    prediction = predict_next_score(db, user_id)
    weekly_gain = prediction.get("weeklyImprovement") or 1

    estimated_weeks = None
    if readiness_pct < 80 and weekly_gain > 0:
        estimated_weeks = int(np.ceil((80 - readiness_pct) / max(weekly_gain, 0.5)))
    elif readiness_pct >= 80:
        estimated_weeks = 0

    message = (
        f"You are exam-ready at {readiness_pct}%!"
        if readiness_pct >= 80
        else f"Estimated {estimated_weeks} weeks to reach 80% readiness."
    )

    return {
        "readinessPercentage": readiness_pct,
        "estimatedWeeks": estimated_weeks,
        "targetExam": target_exam or "General",
        "message": message,
    }
