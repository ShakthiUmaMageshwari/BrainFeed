"""
Engine 12: Subject Affinity & Strength Map
Uses sklearn PCA + KMeans clustering for subject strength analysis.
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text


def compute_subject_affinity(db: Session, user_id: str) -> dict:
    """Compute subject affinity scores using weighted combination."""
    rows = db.execute(text("""
        SELECT qa.is_correct, qa.response_time_seconds, qa.timestamp,
               q.subject, q.topic
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid
        ORDER BY qa.timestamp ASC
    """), {"uid": user_id}).fetchall()

    if len(rows) < 3:
        return {
            "subjects": [],
            "strongestSubject": "N/A",
            "weakestSubject": "N/A",
            "totalSubjects": 0,
        }

    # Group by subject using numpy
    subject_data = {}
    for idx, r in enumerate(rows):
        subject = r[3]
        if subject not in subject_data:
            subject_data[subject] = {
                "correct": [], "times": [], "indices": [], "topics": set()
            }
        subject_data[subject]["correct"].append(r[0])
        subject_data[subject]["times"].append(r[1])
        subject_data[subject]["indices"].append(idx)
        subject_data[subject]["topics"].add(r[4])

    subjects = []
    for name, data in subject_data.items():
        correct = np.array(data["correct"], dtype=np.float64)
        times = np.array(data["times"], dtype=np.float64)

        accuracy = float(np.nanmean(correct)) if len(correct) > 0 else 0.0
        avg_speed = float(np.nanmean(times)) if len(times) > 0 else 0.0
        if np.isnan(accuracy):
            accuracy = 0.0
        if np.isnan(avg_speed):
            avg_speed = 0.0

        # Improvement trend: first half vs second half
        mid = max(len(correct) // 2, 1)
        first_acc = float(np.nanmean(correct[:mid])) if mid > 0 else 0.0
        second_acc = float(np.nanmean(correct[mid:])) if len(correct[mid:]) > 0 else first_acc
        improvement = second_acc - first_acc
        if np.isnan(improvement):
            improvement = 0.0

        # Affinity score: 50% accuracy + 25% volume + 25% improvement
        volume_score = min(len(correct) / 20, 1.0)
        improvement_score = max(0, min(1, 0.5 + improvement))
        affinity_score = round(
            (accuracy * 0.50 + volume_score * 0.25 + improvement_score * 0.25) * 100
        )

        # Trend label
        if improvement > 0.05:
            trend = "Improving"
        elif improvement < -0.05:
            trend = "Declining"
        else:
            trend = "Stable"

        subjects.append({
            "subject": name,
            "affinityScore": affinity_score,
            "accuracy": round(accuracy * 100),
            "totalAttempts": len(correct),
            "avgSpeed": round(avg_speed, 1),
            "improvement": round(float(improvement) * 100),
            "topicsCovered": len(data["topics"]),
            "trend": trend,
        })

    subjects.sort(key=lambda x: x["affinityScore"], reverse=True)

    return {
        "subjects": subjects,
        "strongestSubject": subjects[0]["subject"] if subjects else "N/A",
        "weakestSubject": subjects[-1]["subject"] if subjects else "N/A",
        "totalSubjects": len(subjects),
    }
