"""
Engine 3a: Bayesian Knowledge Tracing (BKT)
Tracks the probability that a student "knows" a skill (topic) given their history.

Parameters (Standard defaults):
- P(L0) = Initial probability of knowing (0.1)
- P(T) = Probability of learning transition (0.1)
- P(G) = Probability of guessing correct (0.2)
- P(S) = Probability of slipping (incorrect despite knowing) (0.1)
"""

DEFAULT_PARAMS = {
    "p_init": 0.1,
    "p_transit": 0.1,
    "p_guess": 0.2,
    "p_slip": 0.1
}

def update_bkt(p_known: float, is_correct: bool) -> float:
    """
    Update probability of knowing a skill based on a single observation.
    
    Args:
        p_known: Prior probability of knowledge (from previous step)
        is_correct: Whether the student answered correctly (True/False)
        
    Returns:
        Posterior probability of knowledge
    """
    p_g = DEFAULT_PARAMS["p_guess"]
    p_s = DEFAULT_PARAMS["p_slip"]
    p_t = DEFAULT_PARAMS["p_transit"]
    
    if is_correct:
        # P(L|Correct) = (P(L) * (1-P(S))) / (P(L)*(1-P(S)) + (1-P(L))*P(G))
        prob_given_obs = (p_known * (1 - p_s)) / (p_known * (1 - p_s) + (1 - p_known) * p_g)
    else:
        # P(L|Incorrect) = (P(L) * P(S)) / (P(L)*P(S) + (1-P(L))*(1-P(G)))
        prob_given_obs = (p_known * p_s) / (p_known * p_s + (1 - p_known) * (1 - p_g))
        
    # Apply transition (Learning)
    # P(L_next) = P(L_given_obs) + (1 - P(L_given_obs)) * P(T)
    p_next = prob_given_obs + (1 - prob_given_obs) * p_t
    
    return float(min(0.99, max(0.01, p_next)))

def calculate_topic_mastery_bkt(history: list[bool]) -> float:
    """
    Calculate current mastery probability from a sequence of attempts.
    
    Args:
        history: List of booleans (True=Correct, False=Incorrect) ordered chronologically.
    """
    p = DEFAULT_PARAMS["p_init"]
    for attempt in history:
        p = update_bkt(p, attempt)
    return p
