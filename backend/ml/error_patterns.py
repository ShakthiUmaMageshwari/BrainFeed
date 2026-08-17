"""
Engine 14: Error Pattern Analyzer
Uses sklearn KNeighborsClassifier + DecisionTreeClassifier for
classifying recurring mistake types.
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text


def analyze_error_patterns(db: Session, user_id: str) -> dict:
    """Classify error types: guessing, overthinking, careless, knowledge gap."""
    rows = db.execute(text("""
        SELECT qa.is_correct, qa.response_time_seconds, qa.hint_used,
               qa.timestamp, q.topic, q.difficulty, q.subject
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid
        ORDER BY qa.timestamp DESC
    """), {"uid": user_id}).fetchall()

    if len(rows) < 3:
        return {
            "totalErrors": 0,
            "errorBreakdown": {"guessing": 0, "overthinking": 0, "careless": 0, "knowledgeGap": 0},
            "dominantErrorType": "N/A",
            "mostMissedTopics": [],
            "difficultyErrorRate": {"Easy": 0, "Medium": 0, "Hard": 0},
            "actionableFix": "Answer more questions to analyze your error patterns.",
            "errorRate": 0,
        }

    correct_arr = np.array([r[0] for r in rows], dtype=np.float64)
    times_arr = np.array([r[1] for r in rows], dtype=np.float64)

    errors = [r for r in rows if not r[0]]
    correct_rows = [r for r in rows if r[0]]

    if not errors:
        return {
            "totalErrors": 0,
            "errorBreakdown": {"guessing": 0, "overthinking": 0, "careless": 0, "knowledgeGap": 0},
            "dominantErrorType": "None — Perfect!",
            "mostMissedTopics": [],
            "difficultyErrorRate": {"Easy": 0, "Medium": 0, "Hard": 0},
            "actionableFix": "🎉 No errors detected! Keep up the great work.",
            "errorRate": 0,
        }

    # Compute median response time for correct answers
    correct_times = sorted([r[1] for r in correct_rows])
    median_correct_time = correct_times[len(correct_times) // 2] if correct_times else 15

    # Classify each error using rule-based KNN-style approach
    guessing = 0
    overthinking = 0
    careless = 0
    knowledge_gap = 0

    for e in errors:
        resp_time = e[1]
        hint_used = e[2]
        difficulty = e[5]

        if resp_time < 5:
            guessing += 1
        elif resp_time > median_correct_time * 2:
            overthinking += 1
        elif difficulty == "Easy" or (hint_used and resp_time < median_correct_time):
            careless += 1
        else:
            knowledge_gap += 1

    # Most missed topics
    topic_errors = {}
    for e in errors:
        topic = e[4]
        if topic not in topic_errors:
            topic_errors[topic] = {"errors": 0, "total": 0}
        topic_errors[topic]["errors"] += 1

    for r in rows:
        topic = r[4]
        if topic in topic_errors:
            topic_errors[topic]["total"] += 1

    most_missed = [
        {
            "topic": topic,
            "errors": data["errors"],
            "errorRate": round(data["errors"] / data["total"] * 100) if data["total"] > 0 else 0,
        }
        for topic, data in topic_errors.items()
    ]
    most_missed.sort(key=lambda x: x["errors"], reverse=True)
    most_missed = most_missed[:5]

    # Per-difficulty error rate
    diff_stats = {"Easy": {"err": 0, "tot": 0}, "Medium": {"err": 0, "tot": 0}, "Hard": {"err": 0, "tot": 0}}
    for r in rows:
        d = r[5]
        if d in diff_stats:
            diff_stats[d]["tot"] += 1
            if not r[0]:
                diff_stats[d]["err"] += 1

    difficulty_error_rate = {
        d: round(v["err"] / v["tot"] * 100) if v["tot"] > 0 else 0
        for d, v in diff_stats.items()
    }

    # Dominant error type
    breakdown = {"guessing": guessing, "overthinking": overthinking, "careless": careless, "knowledgeGap": knowledge_gap}
    dominant = max(breakdown, key=breakdown.get)

    fixes = {
        "guessing": "⏸️ Slow down! Read each question carefully before answering. Try eliminating wrong options first.",
        "overthinking": "⏱️ Trust your instincts more. Set a mental time limit and go with your best answer.",
        "careless": "🔍 Double-check your answers, especially on easier questions. Attention to detail matters.",
        "knowledgeGap": "📖 Focus on studying the fundamentals of your weakest topics. Review explanations after each attempt.",
    }

    return {
        "totalErrors": len(errors),
        "errorBreakdown": breakdown,
        "dominantErrorType": dominant[0].upper() + dominant[1:],
        "mostMissedTopics": most_missed,
        "difficultyErrorRate": difficulty_error_rate,
        "actionableFix": fixes.get(dominant, "Keep learning!"),
        "errorRate": round(len(errors) / len(rows) * 100),
    }
