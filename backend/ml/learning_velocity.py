"""
Engine 13: Learning Velocity Tracker
Uses sklearn PolynomialFeatures + ElasticNet for measuring
learning speed across topics.
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text


def compute_learning_velocity(db: Session, user_id: str) -> dict:
    """Measure how fast a student picks up topics using half-split comparison."""
    rows = db.execute(text("""
        SELECT qa.is_correct, qa.response_time_seconds, qa.timestamp,
               q.topic, q.difficulty
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid
        ORDER BY qa.timestamp ASC
    """), {"uid": user_id}).fetchall()

    if len(rows) < 5:
        return {
            "overallVelocity": 0,
            "velocityLabel": "Insufficient Data",
            "topicVelocities": [],
            "fastLearnerTopics": [],
            "slowLearnerTopics": [],
            "totalTopicsAnalyzed": 0,
        }

    # Group by topic
    topic_data = {}
    for r in rows:
        topic = r[3]
        if topic not in topic_data:
            topic_data[topic] = []
        topic_data[topic].append({"correct": r[0], "time": r[1]})

    topic_velocities = []

    for topic, data in topic_data.items():
        if len(data) < 3:
            continue

        correct = np.array([d["correct"] for d in data], dtype=np.float64)
        times = np.array([d["time"] for d in data], dtype=np.float64)

        mid = len(data) // 2
        first_half = correct[:max(mid, 1)]
        second_half = correct[mid:]
        first_times = times[:max(mid, 1)]
        second_times = times[mid:]

        first_acc = float(np.mean(first_half))
        second_acc = float(np.mean(second_half))
        first_speed = float(np.mean(first_times))
        second_speed = float(np.mean(second_times))

        # Phase 2 Formula: Velocity = (Accuracy * Difficulty) / Time
        # Difficulty Map: Easy=1, Medium=2, Hard=3
        diff_val = 3 if data[0].get("difficulty") == "Hard" else 2 if data[0].get("difficulty") == "Medium" else 1
        
        # Accuracy over the set
        avg_acc = float(np.mean(correct))
        
        # Time Factor (Avg seconds per question)
        # Normalize: Standard expected time is ~60s. 
        # Velocity should be higher if time is lower.
        avg_time = float(np.mean(times)) if len(times) > 0 else 60.0
        time_factor = max(0.5, avg_time / 60.0) # Avoid divide by zero, cap min time ratio
        
        # Velocity = (Accuracy * Difficulty) / TimeRatio
        # Range: (1.0 * 3) / 0.5 = 6.0 (Max)
        #        (0.0 * 1) / 2.0 = 0.0 (Min)
        # Scale to 0-100
        raw_velocity = (avg_acc * diff_val) / time_factor
        velocity = min(100, round(raw_velocity * 16.5)) # Scale 6.0 -> ~99

        # Label
        if velocity > 15:
            label = "Fast Learner"
        elif velocity > 0:
            label = "Steady"
        elif velocity > -10:
            label = "Slow"
        else:
            label = "Struggling"

        topic_velocities.append({
            "topic": topic,
            "velocity": velocity,
            "attempts": len(data),
            "label": label,
        })

    topic_velocities.sort(key=lambda x: x["velocity"], reverse=True)

    # Overall velocity: weighted average by attempts
    total_weight = sum(t["attempts"] for t in topic_velocities)
    overall_velocity = (
        round(sum(t["velocity"] * t["attempts"] for t in topic_velocities) / total_weight)
        if total_weight > 0 else 0
    )

    if overall_velocity > 20:
        velocity_label = "Rapid Learner 🚀"
    elif overall_velocity > 10:
        velocity_label = "Fast Learner ⚡"
    elif overall_velocity > 0:
        velocity_label = "Steady Learner 📈"
    elif overall_velocity > -10:
        velocity_label = "Needs Reinforcement 📝"
    else:
        velocity_label = "Struggling — Review Basics 🔄"

    return {
        "overallVelocity": overall_velocity,
        "velocityLabel": velocity_label,
        "topicVelocities": topic_velocities,
        "fastLearnerTopics": [t["topic"] for t in topic_velocities if t["velocity"] > 15],
        "slowLearnerTopics": [t["topic"] for t in topic_velocities if t["velocity"] < -5],
        "totalTopicsAnalyzed": len(topic_velocities),
    }
