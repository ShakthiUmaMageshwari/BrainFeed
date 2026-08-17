"""
Engine 9: AI-Powered Recommendation Engine
Hybrid scoring using NumPy feature matrices + pandas ranking.
Weak topics (40%) + exam priority (30%) + revision urgency (20%) + engagement (10%)
"""
import numpy as np
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.ml.forgetting_curve import compute_retention


def get_recommendations(db: Session, user_id: str, target_exam: str, limit: int = 10) -> list:
    """Generate topic recommendations using hybrid scoring."""
    # Get all available topics
    all_topics = db.execute(text("""
        SELECT DISTINCT topic, subject FROM questions
    """)).fetchall()

    # Get mastery data
    mastery_rows = db.execute(text("""
        SELECT topic, mastery_score FROM mastery_logs WHERE user_id = :uid
    """), {"uid": user_id}).fetchall()
    mastery_map = {r[0]: r[1] for r in mastery_rows}

    # Get attempt counts per topic
    attempt_rows = db.execute(text("""
        SELECT q.topic, COUNT(*) as cnt
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        WHERE qa.user_id = :uid
        GROUP BY q.topic
    """), {"uid": user_id}).fetchall()
    attempt_map = {r[0]: r[1] for r in attempt_rows}

    scored = []
    for t in all_topics:
        topic, subject = t[0], t[1]
        mastery = mastery_map.get(topic, 0)
        attempts = attempt_map.get(topic, 0)

        # 1. Weak topic priority (40%)
        weak_score = max(0, 100 - mastery)

        # 2. Exam priority (30%)
        exam_score = 30
        if target_exam:
            exam_row = db.execute(text("""
                SELECT COUNT(*) as cnt FROM questions
                WHERE topic = :topic AND exam_tag LIKE :tag
            """), {"topic": topic, "tag": f"%{target_exam}%"}).fetchone()
            exam_score = 100 if exam_row and exam_row[0] > 0 else 10

        # 3. Revision urgency (20%)
        retention = compute_retention(db, user_id, topic)
        revision_score = (1 - retention["retention"]) * 100 if retention.get("needsRevision") else 0

        # 4. Engagement / freshness (10%)
        engagement_score = 80 if attempts == 0 else max(0, 60 - attempts * 2)

        total_score = (
            weak_score * 0.4 +
            exam_score * 0.3 +
            revision_score * 0.2 +
            engagement_score * 0.1
        )

        # Determine reason
        if mastery < 40:
            reason = "Weak topic"
        elif retention.get("needsRevision"):
            reason = "Needs revision"
        elif attempts == 0:
            reason = "New topic"
        else:
            reason = "Exam priority"

        scored.append({
            "topic": topic,
            "subject": subject,
            "score": round(total_score),
            "mastery": mastery,
            "isRevision": retention.get("needsRevision", False),
            "reason": reason,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


def get_recommended_questions(db: Session, user_id: str, target_exam: str, limit: int = 5) -> list:
    """Get recommended questions based on topic recommendations."""
    topics = get_recommendations(db, user_id, target_exam, 3)

    if not topics:
        rows = db.execute(text("""
            SELECT * FROM questions ORDER BY RANDOM() LIMIT :lim
        """), {"lim": limit}).fetchall()
        return [_row_to_question(r) for r in rows]

    topic_names = [t["topic"] for t in topics]
    placeholders = ", ".join([f":t{i}" for i in range(len(topic_names))])
    params = {f"t{i}": name for i, name in enumerate(topic_names)}
    params["uid"] = user_id
    params["lim"] = limit

    rows = db.execute(text(f"""
        SELECT q.* FROM questions q
        WHERE q.topic IN ({placeholders})
        AND q.id NOT IN (
            SELECT question_id FROM question_attempts
            WHERE user_id = :uid
        )
        ORDER BY RANDOM()
        LIMIT 50
    """), params).fetchall()

    # If we don't have enough new questions, fill with older ones (attempted > 3 days ago)
    if len(rows) < limit:
        needed = limit - len(rows)
        params["lim"] = needed
        fallback_rows = db.execute(text(f"""
            SELECT q.* FROM questions q
            WHERE q.topic IN ({placeholders})
            AND q.id NOT IN (
                SELECT question_id FROM question_attempts
                WHERE user_id = :uid AND timestamp > datetime('now', '-3 days')
            )
            AND q.id NOT IN (
                SELECT id FROM questions WHERE id IN ({','.join([f"'{r.id}'" for r in rows]) if rows else "''"})
            )
            ORDER BY RANDOM()
            LIMIT 20
        """), params).fetchall()
        rows.extend(fallback_rows)

    from backend.ml.irt import get_irt_probability, standardize_difficulty
    import math

    # Score candidates using IRT
    scored_candidates = []
    
    # Pre-fetch mastery for these topics to calc Theta
    mastery_map = {t["topic"]: t["mastery"] for t in topics}

    for r in rows:
        q = _row_to_question(r)
        topic = q.get("topic")
        
        # Calculate Theta (User Ability) from Mastery
        # Mastery is 0-100. Convert to 0.01-0.99 for logit.
        m = max(1, min(99, mastery_map.get(topic, 50))) / 100.0
        theta = math.log(m / (1 - m))
        
        # Calculate Beta (Question Difficulty)
        beta = standardize_difficulty(q.get("difficulty", "Medium"))
        
        # P(Correct)
        prob_correct = get_irt_probability(theta, beta)
        
        # Optimality: Target 70% success rate (Zone of Proximal Development)
        # Score = 1 - abs(prob - 0.7) -> Closer to 1 is better
        optimality = 1.0 - abs(prob_correct - 0.70)
        
        matching_topic = next((t for t in topics if t["topic"] == topic), None)
        q["recommendationReason"] = matching_topic["reason"] if matching_topic else "Recommended"
        q["irtScore"] = optimality
        
        scored_candidates.append(q)

    # Sort by IRT optimality
    scored_candidates.sort(key=lambda x: x["irtScore"], reverse=True)
    
    return scored_candidates[:limit]


def _row_to_question(row) -> dict:
    """Convert a raw DB row to a question dict."""
    if hasattr(row, "_mapping"):
        d = dict(row._mapping)
    else:
        keys = ["id", "subject", "topic", "subtopic", "exam_tag", "difficulty",
                "question_text", "options", "correct_answer", "explanation", "created_at"]
        d = dict(zip(keys, row))

    if isinstance(d.get("options"), str):
        try:
            d["options"] = json.loads(d["options"])
        except (json.JSONDecodeError, TypeError):
            pass
    return d
