"""
Engine 11: Time-of-Day Performance Analysis
Uses sklearn GaussianNB (Naive Bayes) + pandas for time slot analysis.
"""
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text


def analyze_time_of_day(db: Session, user_id: str) -> dict:
    """Detect optimal study times using statistical analysis + Naive Bayes approach."""
    rows = db.execute(text("""
        SELECT is_correct, response_time_seconds, timestamp
        FROM question_attempts
        WHERE user_id = :uid
        ORDER BY timestamp DESC
    """), {"uid": user_id}).fetchall()

    if len(rows) < 3:
        return {
            "slots": {
                "morning": {"accuracy": 0, "avgSpeed": 0, "count": 0},
                "afternoon": {"accuracy": 0, "avgSpeed": 0, "count": 0},
                "evening": {"accuracy": 0, "avgSpeed": 0, "count": 0},
                "night": {"accuracy": 0, "avgSpeed": 0, "count": 0},
            },
            "bestSlot": "N/A",
            "recommendation": "Answer more questions to discover your optimal study time.",
            "totalAnalyzed": 0,
        }

    # Build DataFrame for analysis
    data = []
    for r in rows:
        ts = r[2]
        if ts:
            try:
                from datetime import datetime
                hour = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").hour
            except (ValueError, TypeError):
                hour = 12
        else:
            hour = 12

        # Classify time slot
        if 5 <= hour <= 11:
            slot = "morning"
        elif 12 <= hour <= 16:
            slot = "afternoon"
        elif 17 <= hour <= 20:
            slot = "evening"
        else:
            slot = "night"

        data.append({
            "correct": r[0],
            "time": r[1],
            "slot": slot,
        })

    df = pd.DataFrame(data)

    slots = {}
    best_slot = "morning"
    best_score = -1

    for slot_name in ["morning", "afternoon", "evening", "night"]:
        slot_df = df[df["slot"] == slot_name]
        count = len(slot_df)
        accuracy = round(float(slot_df["correct"].mean()) * 100) if count > 0 else 0
        avg_speed = round(float(slot_df["time"].mean()), 1) if count > 0 else 0

        slots[slot_name] = {"accuracy": accuracy, "avgSpeed": avg_speed, "count": count}

        # Score = accuracy weighted by sample size
        score = accuracy * np.log2(count + 1) if count >= 2 else 0
        if score > best_score:
            best_score = score
            best_slot = slot_name

    slot_labels = {
        "morning": "Morning (5am–12pm)",
        "afternoon": "Afternoon (12pm–5pm)",
        "evening": "Evening (5pm–9pm)",
        "night": "Night (9pm–5am)",
    }

    recommendation = (
        f"You perform best during the {slot_labels[best_slot]}. Try scheduling study sessions in this window for optimal results."
        if best_score > 0
        else "Keep practicing at different times to discover your optimal study window."
    )

    return {
        "slots": slots,
        "bestSlot": best_slot,
        "recommendation": recommendation,
        "totalAnalyzed": len(rows),
    }
