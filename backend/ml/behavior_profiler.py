"""
Engine 4: Learning Behavior Profiling (sklearn KMeans Clustering)
Classifies users into learning types using StandardScaler + KMeans.
"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from sqlalchemy import text

# Predefined profile labels
PROFILE_NAMES = [
    "Fast Accurate Performer",
    "Slow Analytical Learner",
    "High Guesser",
    "Struggling Beginner",
    "Inconsistent User",
]

PROFILE_CENTERS = np.array([
    [0.85, 15, 0.1, 0.9],   # Fast Accurate Performer
    [0.75, 45, 0.05, 0.7],  # Slow Analytical Learner
    [0.4, 5, 0.3, 0.3],     # High Guesser
    [0.3, 35, 0.2, 0.2],    # Struggling Beginner
    [0.55, 25, 0.35, 0.4],  # Inconsistent User
])

PROFILE_DESCRIPTIONS = {
    "Fast Accurate Performer": "You solve questions quickly and accurately. Keep pushing to harder levels!",
    "Slow Analytical Learner": "You take your time and think carefully. Your accuracy is solid — try to improve speed gradually.",
    "High Guesser": "Your response times suggest guessing. Slow down and read questions thoroughly.",
    "Struggling Beginner": "Everyone starts somewhere! Focus on building fundamentals with easier questions.",
    "Inconsistent User": "Your performance varies. Try to maintain steady practice for better consistency.",
}


def classify_user(db: Session, user_id: str) -> dict:
    """Classify user into a learning profile using sklearn KMeans."""
    rows = db.execute(text("""
        SELECT is_correct, response_time_seconds
        FROM question_attempts
        WHERE user_id = :uid
        ORDER BY timestamp DESC
        LIMIT 30
    """), {"uid": user_id}).fetchall()

    if len(rows) < 5:
        return {"type": "New User", "confidence": 0, "description": "Not enough data to classify."}

    correct = np.array([r[0] for r in rows], dtype=np.float64)
    times = np.array([r[1] for r in rows], dtype=np.float64)

    # Compute features
    accuracy = float(np.mean(correct))
    avg_time = float(np.mean(times))
    time_variance = float(np.std(times) / 30.0)
    time_variance = min(1.0, time_variance)

    # Streak ratio
    max_streak = 0
    current_streak = 0
    for c in correct:
        if c:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    streak_ratio = max_streak / len(correct)

    # Feature vector
    user_features = np.array([[accuracy, avg_time, time_variance, streak_ratio]])

    # Use sklearn KMeans with predefined centers
    # We fit KMeans on the profile centers, then predict the user's cluster
    scaler = StandardScaler()
    all_data = np.vstack([PROFILE_CENTERS, user_features])

    # Normalize features for distance calculation
    scaled_data = scaler.fit_transform(all_data)
    scaled_centers = scaled_data[:5]
    scaled_user = scaled_data[5:]

    # Fit KMeans on the profile centers
    kmeans = KMeans(n_clusters=5, init=scaled_centers, n_init=1, max_iter=1, random_state=42)
    kmeans.fit(scaled_centers)

    # Predict cluster for user
    cluster_idx = kmeans.predict(scaled_user)[0]

    # Compute confidence as 1 - normalized distance to nearest center
    distances = np.linalg.norm(scaled_centers - scaled_user, axis=1)
    min_dist = float(distances[cluster_idx])
    confidence = max(0.0, min(1.0, 1.0 - min_dist / (np.max(distances) + 1e-6)))

    profile_name = PROFILE_NAMES[cluster_idx]

    return {
        "type": profile_name,
        "confidence": round(confidence, 2),
        "features": {
            "accuracy": round(accuracy * 100),
            "avgTime": round(avg_time),
            "speedVariance": round(time_variance * 100),
            "streakRatio": round(streak_ratio * 100),
        },
        "description": PROFILE_DESCRIPTIONS.get(profile_name, "Keep learning!"),
    }
