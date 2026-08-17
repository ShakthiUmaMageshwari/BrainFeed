"""
Analytics routes: Dashboard endpoint
Aggregates all 15 ML engines into a single comprehensive response.
Key names MUST match what the frontend HTML expects:
  prediction, learningProfile, engagement, performanceTrend,
  cognitiveLoad, dropoffRisk, recommendations, examReadiness (array),
  timeOfDay, subjectAffinity, learningVelocity, errorPatterns,
  sessionQuality, mastery, features
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from backend.db.database import get_db
from backend.utils.cache import cache

from backend.ml.mastery_model import get_all_mastery
from backend.ml.predictive_engine import predict_next_score, estimate_readiness_date
from backend.ml.adaptive_difficulty import get_adaptive_difficulty
from backend.ml.behavior_profiler import classify_user
from backend.ml.exam_readiness import compute_exam_readiness
from backend.ml.forgetting_curve import get_revision_topics
from backend.ml.dropoff_risk import compute_dropoff_risk
from backend.ml.recommendation_engine import get_recommendations
from backend.ml.cognitive_load import analyze_cognitive_load
from backend.ml.time_of_day import analyze_time_of_day
from backend.ml.subject_affinity import compute_subject_affinity
from backend.ml.learning_velocity import compute_learning_velocity
from backend.ml.error_patterns import analyze_error_patterns
from backend.ml.session_quality import compute_session_quality
from backend.ml.feature_engineering import compute_features
from backend.ml.model_monitor import compute_model_metrics

router = APIRouter()


def _build_engagement(db: Session, user_id: str) -> dict:
    """Build engagement stats from raw data (streak, accuracy, totalAttempts)."""
    row = db.execute(text("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
        FROM question_attempts
        WHERE user_id = :uid
    """), {"uid": user_id}).fetchone()

    total = row[0] if row else 0
    correct = row[1] if row else 0
    accuracy = round(correct / total * 100) if total > 0 else 0

    # Streak: count consecutive days with at least 1 attempt
    days = db.execute(text("""
        SELECT DISTINCT DATE(timestamp) as d
        FROM question_attempts
        WHERE user_id = :uid
        ORDER BY d DESC
    """), {"uid": user_id}).fetchall()

    streak = 0
    if days:
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        for i, d in enumerate(days):
            day_date = datetime.strptime(d[0], "%Y-%m-%d").date()
            expected = today - timedelta(days=i)
            if day_date == expected:
                streak += 1
            else:
                break

    return {
        "streak": streak,
        "overallAccuracy": accuracy,
        "totalAttempts": total,
    }


def _build_performance_trend(db: Session, user_id: str) -> list:
    """Build daily accuracy trend for the last 14 days."""
    rows = db.execute(text("""
        SELECT DATE(timestamp) as day,
               COUNT(*) as total,
               SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
        FROM question_attempts
        WHERE user_id = :uid
        GROUP BY DATE(timestamp)
        ORDER BY day DESC
        LIMIT 14
    """), {"uid": user_id}).fetchall()

    trend = []
    for r in reversed(rows):
        accuracy = round(r[2] / r[1] * 100) if r[1] > 0 else 0
        trend.append({"day": r[0], "accuracy": accuracy, "total": r[1]})
    return trend


@router.get("/dashboard")
def get_dashboard(
    userId: str = Query(...),
    targetExam: Optional[str] = Query("GATE"),
    db: Session = Depends(get_db),
):
    try:
        if not userId:
            raise HTTPException(status_code=400, detail="userId is required.")

        # --- Engine 1: Mastery (Cached) ---
        mastery_key = f"mastery:{userId}"
        mastery = cache.get(mastery_key)
        if not mastery:
            mastery = get_all_mastery(db, userId)
            cache.set(mastery_key, mastery, ttl_seconds=600)  # 10 min cache

        # --- Engine 2: Prediction (Cached) ---
        pred_key = f"prediction:{userId}"
        predictions = cache.get(pred_key)
        if not predictions:
            predictions = predict_next_score(db, userId)
            cache.set(pred_key, predictions, ttl_seconds=600)

        adaptive = get_adaptive_difficulty(db, userId)
        behavior = classify_user(db, userId)
        cognitive = analyze_cognitive_load(db, userId)
        time_analysis = analyze_time_of_day(db, userId)
        affinity = compute_subject_affinity(db, userId)
        velocity = compute_learning_velocity(db, userId)
        errors = analyze_error_patterns(db, userId)
        session_quality = compute_session_quality(db, userId)
        features = compute_features(db, userId)

        # --- Engine 5: Exam Readiness (Cached) ---
        readiness_key = f"readiness:{userId}"
        exam_readiness_list = cache.get(readiness_key)
        if not exam_readiness_list:
            exam_readiness_list = []
            for exam in ["GATE", "JEE", "CAT", "UPSC"]:
                exam_readiness_list.append(compute_exam_readiness(db, userId, exam))
            cache.set(readiness_key, exam_readiness_list, ttl_seconds=600)

        # Forgetting curve / revision recommendations
        revision = get_revision_topics(db, userId)
        recommendations = get_recommendations(db, userId, targetExam or "GATE")
        dropoff = compute_dropoff_risk(db, userId)

        # Build engagement stats
        engagement = _build_engagement(db, userId)

        # Build performance trend
        performance_trend = _build_performance_trend(db, userId)
        
        # Model Health (Admin/Dev feature, but exposed here for demo)
        model_health = compute_model_metrics(db)

        # ===== RESPONSE: key names MUST match the frontend HTML =====
        return {
            # Engine 1: Mastery
            "mastery": mastery,

            # Engine 2: Prediction — frontend reads data.prediction
            "prediction": predictions,
            
            # Model Health (New)
            "modelHealth": model_health,

            # Engine 3: Adaptive difficulty
            "adaptiveDifficulty": adaptive,

            # Engine 4: Learning Profile — frontend reads data.learningProfile
            "learningProfile": behavior,

            # Engine 5: Exam Readiness — frontend expects ARRAY
            "examReadiness": exam_readiness_list,

            # Engine 6: Forgetting curve
            "revisionTopics": revision,

            # Engine 7: Drop-off risk
            "dropoffRisk": dropoff,

            # Engine 9: Recommendations
            "recommendations": recommendations,

            # Engine 10: Cognitive Load
            "cognitiveLoad": cognitive,

            # Engine 11: Time of Day
            "timeOfDay": time_analysis,

            # Engine 12: Subject Affinity
            "subjectAffinity": affinity,

            # Engine 13: Learning Velocity
            "learningVelocity": velocity,

            # Engine 14: Error Patterns
            "errorPatterns": errors,

            # Engine 15: Session Quality
            "sessionQuality": session_quality,

            # Engine 16: Feature Engineering
            "features": features,

            # Engagement stats — frontend reads data.engagement
            "engagement": engagement,

            # Performance trend — frontend reads data.performanceTrend
            "performanceTrend": performance_trend,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Analytics] Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate analytics: {str(e)}")
