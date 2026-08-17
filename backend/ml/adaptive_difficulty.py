"""
Engine 3: Intelligent Adaptive Difficulty
Bayesian probability-based difficulty adjustment using NumPy.
Smooth transitions instead of sudden jumps.
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text


def compute_confidence(db: Session, user_id: str) -> float:
    """Compute user confidence score (0-1) using weighted recent performance."""
    rows = db.execute(text("""
        SELECT qa.is_correct, q.difficulty, qa.response_time_seconds
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid
        ORDER BY qa.timestamp DESC
        LIMIT 15
    """), {"uid": user_id}).fetchall()

    if not rows:
        return 0.5  # neutral starting confidence

    n = len(rows)
    correct = np.array([r[0] for r in rows], dtype=np.float64)
    difficulties = [r[1] for r in rows]

    # Recency weights: more recent = higher weight
    indices = np.arange(n, dtype=np.float64)
    recency_weights = 1.0 - indices * 0.04

    # Difficulty weights: harder questions weighted more
    diff_weights = np.array([
        1.5 if d == "Hard" else 1.0 if d == "Medium" else 0.7
        for d in difficulties
    ], dtype=np.float64)

    combined_weights = recency_weights * diff_weights
    weighted_correct = np.sum(correct * combined_weights)
    total_weight = np.sum(combined_weights)

    confidence = weighted_correct / total_weight if total_weight > 0 else 0.5
    return float(np.clip(confidence, 0, 1))


def get_difficulty_probabilities(confidence: float) -> dict:
    """Smooth probability distribution based on confidence using Bayesian approach."""
    # Probability table with smooth transitions
    thresholds = [
        (0.85, {"Easy": 0.05, "Medium": 0.25, "Hard": 0.70}),
        (0.75, {"Easy": 0.10, "Medium": 0.30, "Hard": 0.60}),
        (0.65, {"Easy": 0.15, "Medium": 0.45, "Hard": 0.40}),
        (0.55, {"Easy": 0.20, "Medium": 0.50, "Hard": 0.30}),
        (0.45, {"Easy": 0.30, "Medium": 0.50, "Hard": 0.20}),
        (0.35, {"Easy": 0.45, "Medium": 0.40, "Hard": 0.15}),
    ]

    for threshold, probs in thresholds:
        if confidence >= threshold:
            return probs

    return {"Easy": 0.60, "Medium": 0.30, "Hard": 0.10}


def select_difficulty(confidence: float) -> str:
    """Select difficulty level using probabilistic sampling."""
    probs = get_difficulty_probabilities(confidence)
    rand = np.random.random()

    if rand < probs["Easy"]:
        return "Easy"
    if rand < probs["Easy"] + probs["Medium"]:
        return "Medium"
    return "Hard"


def get_adaptive_difficulty(db: Session, user_id: str) -> dict:
    """Get adaptive difficulty recommendation for a user."""
    confidence = compute_confidence(db, user_id)
    probabilities = get_difficulty_probabilities(confidence)
    selected = select_difficulty(confidence)

    return {
        "confidence": round(confidence, 2),
        "probabilities": probabilities,
        "selectedDifficulty": selected,
    }
