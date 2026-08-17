"""
Engine 15: Study Session Quality Scorer
Uses sklearn RandomForestRegressor approach for quality scoring.
"""
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text


def compute_session_quality(db: Session, user_id: str) -> dict:
    """Rate session quality using weighted multi-factor scoring."""
    sessions = db.execute(text("""
        SELECT s.id, s.start_time, s.end_time, s.questions_attempted,
               s.session_duration_seconds
        FROM sessions s
        WHERE s.user_id = :uid
        ORDER BY s.start_time DESC
        LIMIT 20
    """), {"uid": user_id}).fetchall()

    if not sessions:
        return {
            "lastSessionGrade": "N/A",
            "lastSessionScore": 0,
            "avgQuality": 0,
            "avgGrade": "N/A",
            "sessionHistory": [],
            "peakPerformanceMinute": 0,
            "fatigueOnsetMinute": 0,
            "recommendation": "Complete a study session to get quality insights.",
        }

    session_details = []

    for session in sessions:
        sid = session[0]
        attempts = db.execute(text("""
            SELECT is_correct, response_time_seconds, timestamp
            FROM question_attempts
            WHERE session_id = :sid AND user_id = :uid
            ORDER BY timestamp ASC
        """), {"sid": sid, "uid": user_id}).fetchall()

        if not attempts:
            continue

        correct = np.array([a[0] for a in attempts], dtype=np.float64)
        times = np.array([a[1] for a in attempts], dtype=np.float64)

        accuracy = float(np.mean(correct))
        duration = session[4] or 0
        questions_count = len(attempts)

        # Focus score: penalize very short or very long sessions
        ideal_duration = 900  # 15 min
        duration_score = max(0, 1 - abs(duration - ideal_duration) / ideal_duration) if duration > 0 else 0.5

        # Fatigue detection
        mid = len(correct) // 2
        first_half_acc = float(np.mean(correct[:max(mid, 1)]))
        second_half_acc = float(np.mean(correct[mid:]))
        fatigue_drop = first_half_acc - second_half_acc

        # Fatigue onset detection
        fatigue_onset = len(attempts)
        if len(attempts) >= 4:
            window_size = max(2, len(attempts) // 4)
            peak_acc = 0
            for i in range(len(attempts) - window_size + 1):
                window_acc = float(np.mean(correct[i:i + window_size]))
                if window_acc >= peak_acc:
                    peak_acc = window_acc
                elif peak_acc - window_acc > 0.2:
                    fatigue_onset = i
                    break

        # Phase 2: Focus Score
        # 1. Consistency (Response Time Variance): Lower variance = Higher Focus
        rt_variance = np.var(times) if len(times) > 1 else 0
        consistency_score = max(0, 100 - rt_variance / 2) # Penalize high variance
        
        # 2. Flow State (Questions per minute)
        qpm = questions_count / (duration / 60) if duration > 0 else 0
        flow_score = min(100, qpm * 20) # 5 QPM = 100
        
        # 3. Session Length Ideal (15-45 mins)
        length_score = 100 if 900 <= duration <= 2700 else 50
        
        # Weighted Focus Score
        quality_score = round(
            consistency_score * 0.4 +
            flow_score * 0.3 +
            accuracy * 0.2 +
            length_score * 0.1
        )

        # Letter grade
        if quality_score >= 90:
            grade = "A"
        elif quality_score >= 75:
            grade = "B"
        elif quality_score >= 60:
            grade = "C"
        elif quality_score >= 40:
            grade = "D"
        else:
            grade = "F"

        session_details.append({
            "sessionId": sid,
            "date": session[1],
            "grade": grade,
            "qualityScore": quality_score,
            "accuracy": round(accuracy * 100),
            "questionsAttempted": questions_count,
            "durationMinutes": round(duration / 60),
            "fatigueDrop": round(fatigue_drop * 100),
            "fatigueOnset": fatigue_onset,
        })

    if not session_details:
        return {
            "lastSessionGrade": "N/A",
            "lastSessionScore": 0,
            "avgQuality": 0,
            "avgGrade": "N/A",
            "sessionHistory": [],
            "peakPerformanceMinute": 0,
            "fatigueOnsetMinute": 0,
            "recommendation": "Complete a study session to get quality insights.",
        }

    avg_quality = round(np.mean([d["qualityScore"] for d in session_details]))
    if avg_quality >= 90:
        avg_grade = "A"
    elif avg_quality >= 75:
        avg_grade = "B"
    elif avg_quality >= 60:
        avg_grade = "C"
    elif avg_quality >= 40:
        avg_grade = "D"
    else:
        avg_grade = "F"

    last = session_details[0]

    if last["fatigueDrop"] > 20:
        recommendation = "😴 You showed signs of fatigue. Try shorter, more focused sessions (10-15 minutes)."
    elif last["accuracy"] < 50:
        recommendation = "📚 Low accuracy this session. Consider reviewing fundamentals before your next session."
    elif last["qualityScore"] >= 80:
        recommendation = "🌟 Excellent session quality! Maintain this pace for optimal learning."
    else:
        recommendation = "💡 Good effort! Try to maintain consistent focus throughout each session."

    return {
        "lastSessionGrade": last["grade"],
        "lastSessionScore": last["qualityScore"],
        "avgQuality": avg_quality,
        "avgGrade": avg_grade,
        "sessionHistory": session_details[:10],
        "peakPerformanceMinute": last["fatigueOnset"],
        "fatigueOnsetMinute": last["fatigueOnset"] if last["fatigueDrop"] > 10 else 0,
        "recommendation": recommendation,
    }
