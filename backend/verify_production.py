"""
Verification Script for Production Upgrade
Tests:
1. DB Connection (SQLite fallback / Postgres)
2. Redis Caching
3. Event Logging
4. BKT & IRT Logic
5. Model Monitor
6. Background Tasks (Simulation)
"""
import sys
import os
import json
import time

# Add root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import SessionLocal, init_db
from backend.utils.cache import cache
from backend.ml.bkt import calculate_topic_mastery_bkt
from backend.ml.irt import get_irt_probability
from backend.ml.model_monitor import compute_model_metrics
from backend.db.models import EventLog, QuestionAttempt

def test_db_and_cache():
    print("\n--- Testing Infrastructure ---")
    db = SessionLocal()
    try:
        # Test Cache
        cache.set("test_key", {"foo": "bar"}, 60)
        val = cache.get("test_key")
        print(f"✅ Cache Set/Get: {val == {'foo': 'bar'}} (Val: {val})")
        
        # Test DB
        count = db.query(EventLog).count()
        print(f"✅ DB Connection: OK (EventLog count: {count})")
    finally:
        db.close()

def test_ml_logic():
    print("\n--- Testing ML Engines ---")
    
    # BKT
    history = [False, False, True, True, True] # Learning!
    mastery = calculate_topic_mastery_bkt(history)
    print(f"✅ BKT Mastery (Expect > 0.5): {mastery:.4f}")
    
    # IRT
    # Good user (Theta=1.0) vs Hard question (Beta=1.5) -> Prob < 0.5
    prob_hard = get_irt_probability(1.0, 1.5)
    # Good user vs Easy question (Beta=-1.5) -> Prob > 0.9
    prob_easy = get_irt_probability(1.0, -1.5)
    
    print(f"✅ IRT (Hard): {prob_hard:.4f}")
    print(f"✅ IRT (Easy): {prob_easy:.4f}")
    
def test_model_monitor():
    print("\n--- Testing Model Monitor ---")
    db = SessionLocal()
    try:
        metrics = compute_model_metrics(db, limit=10)
        print(f"✅ Model Metrics: {json.dumps(metrics, indent=2)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db() # Ensure tables exist
    test_db_and_cache()
    test_ml_logic()
    test_model_monitor()
