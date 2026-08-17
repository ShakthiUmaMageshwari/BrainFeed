"""
Engine 3b: Item Response Theory (IRT)
Estimates probability of correct response based on User Ability (theta) and Question Difficulty (beta).

Model: 1-Parameter Logistic (Rasch Model)
P(Correct) = 1 / (1 + e^(-(theta - beta)))
"""
import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def get_irt_probability(user_ability: float, question_difficulty: float) -> float:
    """
    Calculate probability of answering correctly.
    
    Args:
        user_ability (theta): Standardized score (-3 to +3)
        question_difficulty (beta): Standardized difficulty (-3 to +3)
    """
    return float(sigmoid(user_ability - question_difficulty))

def estimate_ability(correct_count: int, total_count: int) -> float:
    """
    Estimate user ability (theta) from raw score.
    Simple approximation: Log-odds of accuracy.
    """
    if total_count == 0:
        return 0.0
        
    # Smoothing
    p = (correct_count + 1) / (total_count + 2)
    
    # Logit function: ln(p / (1-p))
    theta = np.log(p / (1 - p))
    
    # Clip to reasonable range (-3 to 3)
    return float(np.clip(theta, -3.0, 3.0))

def standardize_difficulty(difficulty_str: str) -> float:
    """Convert categorical difficulty to IRT beta scale."""
    mapping = {
        "Easy": -1.5,
        "Medium": 0.0,
        "Hard": 1.5
    }
    return mapping.get(difficulty_str, 0.0)
