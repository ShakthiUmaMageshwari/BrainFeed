"""
Phase 2: Student Ranking Engine (ELO)
Implements standard ELO rating system for student vs question.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text

K_FACTOR = 32 # Maximum rating adjustment per game

def get_expected_score(user_rating: int, question_difficulty_rating: int) -> float:
    """
    Calculate expected score (probability of winning) for User vs Question.
    Formula: 1 / (1 + 10 ^ ((RatingB - RatingA) / 400))
    """
    return 1 / (1 + 10 ** ((question_difficulty_rating - user_rating) / 400))

def update_user_elo(db: Session, user_id: str, question_difficulty: str, is_correct: bool) -> int:
    """
    Update user's ELO rating based on question outcome.
    Returns the new rating.
    """
    # 1. Get current rating
    user = db.execute(text("SELECT elo_rating FROM users WHERE id = :uid"), {"uid": user_id}).fetchone()
    if not user:
        return 1200
    
    current_rating = user[0] or 1200
    
    # 2. Determine Question "Rating"
    # Basic mapping: Easy=1000, Medium=1400, Hard=1800
    difficulty_map = {
        "Easy": 1000,
        "Medium": 1400,
        "Hard": 1800
    }
    q_rating = difficulty_map.get(question_difficulty, 1400)
    
    # 3. Calculate Expected Outcome
    expected = get_expected_score(current_rating, q_rating)
    actual = 1.0 if is_correct else 0.0
    
    # 4. Update Formula: R' = R + K * (Actual - Expected)
    new_rating = int(current_rating + K_FACTOR * (actual - expected))
    
    # 5. Persist
    db.execute(text("""
        UPDATE users SET elo_rating = :new_r WHERE id = :uid
    """), {"new_r": new_rating, "uid": user_id})
    db.commit()
    
    return new_rating

def get_leaderboard(db: Session, limit: int = 10) -> list:
    """Get top students by ELO rating."""
    rows = db.execute(text("""
        SELECT full_name, elo_rating FROM users
        ORDER BY elo_rating DESC
        LIMIT :lim
    """), {"lim": limit}).fetchall()
    
    return [
        {"name": r[0], "rating": r[1], "rank": i+1}
        for i, r in enumerate(rows)
    ]
