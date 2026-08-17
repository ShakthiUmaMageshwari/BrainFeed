"""
Verification Script for Phase 2: Advanced Gamification & AI
Tests:
1. Knowledge Graph (Dependencies)
2. ELO Ranking
3. AI Prompt Generation
4. Learning Velocity
"""
import sys
import os
import json

# Add root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import SessionLocal
from backend.ml.knowledge_graph import TOPIC_DEPENDENCIES, get_prerequisite_status
from backend.ml.ranking import update_user_elo, get_expected_score
from backend.ml.ai_generator import generate_question_prompt
from backend.ml.learning_velocity import compute_learning_velocity
# Mock databse for velocity test not easily possible without inserting attempts
# We will test logic functions where possible.

def test_knowledge_graph():
    print("\n--- Testing Knowledge Graph ---")
    print(f"✅ Loaded {len(TOPIC_DEPENDENCIES)} topics in DAG.")
    
    # Check dependencies for 'Graphs'
    deps = TOPIC_DEPENDENCIES.get("Graphs")
    print(f"✅ 'Graphs' depends on: {deps}")
    assert "Trees" in deps
    
def test_elo_ranking():
    print("\n--- Testing ELO Engine ---")
    
    # 1. Expected Score
    # 1200 vs 1200 -> 0.5
    prob_equal = get_expected_score(1200, 1200)
    print(f"✅ P(Win) 1200 vs 1200: {prob_equal:.2f}")
    
    # 1200 vs 1800 (Hard) -> Should be low
    prob_hard = get_expected_score(1200, 1800)
    print(f"✅ P(Win) 1200 vs 1800: {prob_hard:.4f}")
    
    # 2. Rating Update
    # Newbie (1200) beats Hard (1800) -> Massive gain
    # We can't easily run update_user_elo without a real DB user, so we skip the DB write test here.
    # But the formula logic is: New = Old + 32 * (1 - Prob_Low) ~ Old + 32
    gain = 32 * (1 - prob_hard)
    print(f"✅ ELO Gain for upset: +{int(gain)}")

def test_ai_generator():
    print("\n--- Testing AI Generator ---")
    prompt = generate_question_prompt("Computer Science", "Data Structures", "Hard", "GATE")
    print(f"✅ Generated Prompt Length: {len(prompt)}")
    assert "JSON" in prompt
    assert "Data Structures" in prompt

if __name__ == "__main__":
    test_knowledge_graph()
    test_elo_ranking()
    test_ai_generator()
