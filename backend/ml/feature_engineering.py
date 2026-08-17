"""
Feature Engineering Pipeline
Computes derived ML features using pandas DataFrame + NumPy vectorized ops.
"""
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text


def compute_features(db: Session, user_id: str) -> dict:
    """Compute all ML features from raw attempt data using pandas pipeline."""
    rows = db.execute(text("""
        SELECT qa.is_correct, qa.response_time_seconds, qa.timestamp,
               q.topic, q.difficulty, q.subject
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid
        ORDER BY qa.timestamp DESC
    """), {"uid": user_id}).fetchall()

    if not rows:
        return _get_default_features()

    # Build DataFrame
    df = pd.DataFrame(rows, columns=["is_correct", "response_time", "timestamp", "topic", "difficulty", "subject"])
    df["is_correct"] = df["is_correct"].astype(float)
    df["response_time"] = df["response_time"].astype(float)

    n = len(df)

    # Rolling accuracy
    last5_acc = float(df["is_correct"].head(5).mean())
    last10_acc = float(df["is_correct"].head(10).mean())
    overall_acc = float(df["is_correct"].mean())

    # Speed metrics (NumPy)
    times = df["response_time"].values
    avg_time = float(np.mean(times))
    speed_variance = float(np.var(times))

    # Improvement slope (linear regression on rolling accuracy windows)
    window_size = 5
    windows = []
    for i in range(0, n, window_size):
        w = df["is_correct"].iloc[i:i + window_size]
        if len(w) >= 3:
            windows.append(float(w.mean()))
    windows.reverse()  # chronological

    improvement_slope = 0.0
    if len(windows) >= 2:
        x = np.arange(len(windows), dtype=np.float64)
        y = np.array(windows, dtype=np.float64)
        n_win = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x ** 2)
        denom = n_win * sum_x2 - sum_x ** 2
        if denom != 0:
            improvement_slope = float((n_win * sum_xy - sum_x * sum_y) / denom)

    # Consistency score
    consistency_score = 100
    if len(windows) > 1:
        arr = np.array(windows)
        variance = float(np.var(arr))
        consistency_score = max(0, round((1 - np.sqrt(variance)) * 100))

    # Per-difficulty accuracy using pandas groupby
    diff_acc = df.groupby("difficulty")["is_correct"].agg(["sum", "count"])
    difficulty_accuracy = {}
    for d in ["Easy", "Medium", "Hard"]:
        if d in diff_acc.index:
            row = diff_acc.loc[d]
            difficulty_accuracy[d] = round(row["sum"] / row["count"] * 100) if row["count"] > 0 else 0
        else:
            difficulty_accuracy[d] = 0

    # Per-subject accuracy using pandas groupby
    subj_acc = df.groupby("subject")["is_correct"].agg(["sum", "count"])
    subject_accuracy = {
        s: round(row["sum"] / row["count"] * 100) if row["count"] > 0 else 0
        for s, row in subj_acc.iterrows()
    }

    # Streak length
    current_streak = 0
    for val in df["is_correct"].values:
        if val:
            current_streak += 1
        else:
            break

    # Session frequency (last 7 days)
    session_row = db.execute(text("""
        SELECT COUNT(*) as cnt FROM sessions
        WHERE user_id = :uid AND start_time > datetime('now', '-7 days')
    """), {"uid": user_id}).fetchone()
    sessions_per_week = session_row[0] if session_row else 0

    # Guessing probability
    fast_wrong = int(np.sum((times < 5) & (df["is_correct"].values == 0)))
    guessing_probability = round(fast_wrong / max(1, n) * 100)

    return {
        "totalAttempts": n,
        "overallAccuracy": round(overall_acc * 100),
        "rollingAccuracy5": round(last5_acc * 100),
        "rollingAccuracy10": round(last10_acc * 100),
        "avgResponseTime": round(avg_time, 1),
        "speedVariance": round(speed_variance, 1),
        "improvementSlope": round(improvement_slope, 3),
        "consistencyScore": consistency_score,
        "difficultyAccuracy": difficulty_accuracy,
        "subjectAccuracy": subject_accuracy,
        "currentStreak": current_streak,
        "sessionsPerWeek": sessions_per_week,
        "guessingProbability": guessing_probability,
    }


def _get_default_features() -> dict:
    return {
        "totalAttempts": 0,
        "overallAccuracy": 0,
        "rollingAccuracy5": 0,
        "rollingAccuracy10": 0,
        "avgResponseTime": 0,
        "speedVariance": 0,
        "improvementSlope": 0,
        "consistencyScore": 0,
        "difficultyAccuracy": {"Easy": 0, "Medium": 0, "Hard": 0},
        "subjectAccuracy": {},
        "currentStreak": 0,
        "sessionsPerWeek": 0,
        "guessingProbability": 0,
    }
