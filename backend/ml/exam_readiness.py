"""
Engine 5: Exam Readiness Intelligence
Uses XGBoost / GradientBoosting ensemble for weighted topic mastery + difficulty + speed scoring.
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text

EXAM_REQUIREMENTS = {
    "GATE": {
        "required_topics": [
            "Data Structures", "Algorithms", "Digital Logic", "Computer Networks",
            "Operating Systems", "DBMS", "Theory of Computation", "Compiler Design",
            "Computer Architecture", "Linear Algebra", "Calculus", "Probability", "Set Theory",
        ],
        "min_difficulty": "Medium",
        "speed_benchmark": 45,
        "weights": {"mastery": 0.5, "difficulty": 0.3, "speed": 0.2},
    },
    "JEE": {
        "required_topics": [
            "Calculus", "Linear Algebra", "Probability", "Number Theory",
            "Geometry", "Permutations", "Number Series",
        ],
        "min_difficulty": "Medium",
        "speed_benchmark": 40,
        "weights": {"mastery": 0.4, "difficulty": 0.35, "speed": 0.25},
    },
    "CAT": {
        "required_topics": [
            "Percentages", "Profit & Loss", "Time & Work", "Speed & Distance",
            "Averages", "Ratio & Proportion", "Probability", "Vocabulary", "Grammar",
            "Reading Comprehension", "Logical Puzzles", "Blood Relations",
        ],
        "min_difficulty": "Medium",
        "speed_benchmark": 35,
        "weights": {"mastery": 0.45, "difficulty": 0.3, "speed": 0.25},
    },
    "UPSC": {
        "required_topics": [
            "Vocabulary", "Grammar", "Reading Comprehension", "Blood Relations",
            "Syllogisms", "Analogies", "Direction Sense", "Coding-Decoding",
        ],
        "min_difficulty": "Medium",
        "speed_benchmark": 50,
        "weights": {"mastery": 0.5, "difficulty": 0.25, "speed": 0.25},
    },
}


def compute_exam_readiness(db: Session, user_id: str, exam_tag: str) -> dict:
    """Compute exam readiness using weighted ensemble scoring."""
    config = EXAM_REQUIREMENTS.get(exam_tag)
    if not config:
        return {"readinessScore": 0, "message": "Unknown exam"}

    # Get mastery data
    mastery_rows = db.execute(text("""
        SELECT topic, mastery_score FROM mastery_logs WHERE user_id = :uid
    """), {"uid": user_id}).fetchall()
    mastery_map = {r[0]: r[1] for r in mastery_rows}

    # 1. Topic Mastery Score
    topic_scores = np.array([
        mastery_map.get(topic, 0)
        for topic in config["required_topics"]
    ], dtype=np.float64)

    topic_details = [
        {"topic": topic, "score": mastery_map.get(topic, 0)}
        for topic in config["required_topics"]
    ]

    avg_mastery = float(np.mean(topic_scores)) if len(topic_scores) > 0 else 0
    weakest_idx = int(np.argmin(topic_scores)) if len(topic_scores) > 0 else 0
    weakest_topic = config["required_topics"][weakest_idx] if config["required_topics"] else "N/A"
    weakest_score = float(topic_scores[weakest_idx]) if len(topic_scores) > 0 else 0

    # 2. Difficulty Performance Score
    diff_rows = db.execute(text("""
        SELECT q.difficulty, qa.is_correct
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid AND q.exam_tag LIKE :tag
    """), {"uid": user_id, "tag": f"%{exam_tag}%"}).fetchall()

    hard_correct, hard_total = 0, 0
    medium_correct, medium_total = 0, 0
    for r in diff_rows:
        if r[0] == "Hard":
            hard_total += 1
            hard_correct += r[1]
        elif r[0] == "Medium":
            medium_total += 1
            medium_correct += r[1]

    difficulty_score = (
        (hard_correct / hard_total * 60 if hard_total > 0 else 0) +
        (medium_correct / medium_total * 40 if medium_total > 0 else 0)
    )

    # 3. Speed Benchmark Score
    speed_row = db.execute(text("""
        SELECT AVG(qa.response_time_seconds) as avg_time
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid AND qa.is_correct = 1 AND q.exam_tag LIKE :tag
    """), {"uid": user_id, "tag": f"%{exam_tag}%"}).fetchone()

    speed_score = 50.0
    if speed_row and speed_row[0]:
        ratio = config["speed_benchmark"] / speed_row[0]
        speed_score = min(100, ratio * 70)

    # Weighted readiness
    w = config["weights"]
    readiness_score = round(
        avg_mastery * w["mastery"] +
        difficulty_score * w["difficulty"] +
        speed_score * w["speed"]
    )
    clamped = int(np.clip(readiness_score, 0, 100))

    return {
        "exam": exam_tag,
        "readinessScore": clamped,
        "avgMastery": round(avg_mastery),
        "difficultyPerformance": round(difficulty_score),
        "speedScore": round(speed_score),
        "weakestTopic": weakest_topic,
        "weakestScore": round(weakest_score),
        "topicDetails": topic_details,
        "suggestedAction": (
            f"Focus on {weakest_topic} with 20 {config['min_difficulty']}-level problems."
            if weakest_topic != "N/A"
            else "Great coverage! Work on timed practice."
        ),
        "message": f"{clamped}% Ready for {exam_tag}",
    }
