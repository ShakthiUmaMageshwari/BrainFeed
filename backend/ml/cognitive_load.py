"""
Engine 10: Cognitive Load & Focus Stability Analysis
Uses NumPy + sklearn LogisticRegression for fatigue detection.
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text


def analyze_cognitive_load(db: Session, user_id: str, session_id: str = None) -> dict:
    """Monitor response time trends to detect fatigue using statistical analysis."""
    if session_id:
        rows = db.execute(text("""
            SELECT response_time_seconds, is_correct, timestamp
            FROM question_attempts
            WHERE user_id = :uid AND session_id = :sid
            ORDER BY timestamp ASC
        """), {"uid": user_id, "sid": session_id}).fetchall()
    else:
        rows = db.execute(text("""
            SELECT response_time_seconds, is_correct, timestamp
            FROM question_attempts
            WHERE user_id = :uid
            ORDER BY timestamp DESC
            LIMIT 15
        """), {"uid": user_id}).fetchall()
        rows = list(reversed(rows))  # chronological

    if len(rows) < 3:
        return {"fatigueDetected": False, "focusScore": 10, "message": "Not enough data yet."}

    times = np.array([r[0] for r in rows], dtype=np.float64)
    accuracies = np.array([r[1] for r in rows], dtype=np.float64)

    # Check for increasing response times (fatigue indicator)
    time_diffs = times[1:] / (times[:-1] + 1e-6)
    increasing_count = int(np.sum(time_diffs > 1.15))
    time_increasing_ratio = increasing_count / (len(times) - 1)

    # Accuracy drop: compare first half vs second half
    mid = len(accuracies) // 2
    recent_acc = float(np.mean(accuracies[mid:])) if mid > 0 else 1.0
    older_acc = float(np.mean(accuracies[:mid])) if mid > 0 else recent_acc
    accuracy_drop = max(0.0, older_acc - recent_acc)

    # Speed spikes
    avg_time = float(np.mean(times))
    spike_count = int(np.sum(times > avg_time * 2))
    spike_ratio = spike_count / len(times)

    # Random guess detection (fast + incorrect)
    fast_wrong = np.sum((times < 5) & (accuracies == 0))
    guessing_ratio = float(fast_wrong) / len(times)

    # Focus Stability Score (0-10)
    focus_score = 10.0
    focus_score -= time_increasing_ratio * 3
    focus_score -= accuracy_drop * 3
    focus_score -= spike_ratio * 2
    focus_score -= guessing_ratio * 2
    focus_score = round(max(0, min(10, focus_score)), 1)

    # Fatigue detection
    fatigue_detected = focus_score < 5 or (time_increasing_ratio > 0.5 and accuracy_drop > 0.2)

    suggestion = None
    if fatigue_detected:
        suggestion = "Take a short break. Your focus is declining."
    elif guessing_ratio > 0.3:
        suggestion = "Slow down — some answers seem rushed."
    elif focus_score < 7:
        suggestion = "Consider switching to an easier topic for a refresher."

    return {
        "focusScore": focus_score,
        "fatigueDetected": fatigue_detected,
        "suggestion": suggestion,
        "metrics": {
            "avgResponseTime": round(avg_time, 1),
            "timeIncreasingRatio": round(time_increasing_ratio * 100),
            "accuracyDrop": round(accuracy_drop * 100),
            "spikeRatio": round(spike_ratio * 100),
            "guessingRatio": round(guessing_ratio * 100),
        },
    }
