"""
Phase 2: Knowledge Graph & Topic Dependencies
Maps topics to their prerequisites to guide the learning path.
"""
from typing import Dict, List, Set
from sqlalchemy.orm import Session
from sqlalchemy import text

# Directed Acyclic Graph (DAG) of dependencies
# Key: Topic, Value: List of Prerequisite Topics
TOPIC_DEPENDENCIES = {
    # Data Structures
    "Arrays": [],
    "Linked Lists": ["Arrays"],
    "Stacks": ["Arrays", "Linked Lists"],
    "Queues": ["Arrays", "Linked Lists"],
    "Trees": ["Recursion", "Queues"],
    "Graphs": ["Trees", "Stacks", "Queues"],
    "Hashing": ["Arrays"],
    "Heaps": ["Trees", "Arrays"],
    
    # Algorithms
    "Recursion": [],
    "Sorting": ["Arrays"],
    "Searching": ["Arrays", "Sorting"],
    "Dynamic Programming": ["Recursion", "Arrays"],
    "Greedy Algorithms": ["Sorting", "Arrays"],
    
    # OS
    "Process Management": [],
    "Threads": ["Process Management"],
    "CPU Scheduling": ["Process Management", "Queues"],
    "Deadlocks": ["Process Management", "Resource Allocation"],
    "Memory Management": ["Process Management"],
    
    # DBMS
    "ER Model": [],
    "Relational Model": ["ER Model"],
    "SQL": ["Relational Model"],
    "Normalization": ["Relational Model"],
    "Transactions": ["SQL"],
    
    # Networks
    "OSI Model": [],
    "TCP/IP": ["OSI Model"],
    "HTTP/DNS": ["TCP/IP"],
}

def get_prerequisite_status(db: Session, user_id: str) -> Dict[str, str]:
    """
    Check status of all topics for a user based on dependencies.
    Returns dict: { topic: "Locked" | "Ready" | "Completed" }
    """
    # 1. Get user's mastery levels
    rows = db.execute(text("""
        SELECT topic, mastery_score FROM mastery_logs WHERE user_id = :uid
    """), {"uid": user_id}).fetchall()
    
    mastery_map = {r[0]: r[1] for r in rows}
    
    status_map = {}
    
    for topic in TOPIC_DEPENDENCIES.keys():
        score = mastery_map.get(topic, 0)
        
        # If already mastered (e.g. > 60%), it's Completed
        if score >= 60:
            status_map[topic] = "Completed"
            continue
            
        # Check prerequisites
        prereqs = TOPIC_DEPENDENCIES.get(topic, [])
        all_prereqs_met = True
        
        for p in prereqs:
            # Prereq is met if mastery > 40 (Basic understanding)
            if mastery_map.get(p, 0) < 40:
                all_prereqs_met = False
                break
        
        if all_prereqs_met:
            status_map[topic] = "Ready"
        else:
            status_map[topic] = "Locked"
            
    return status_map

def get_next_recommended_topics(db: Session, user_id: str) -> List[str]:
    """Return list of 'Ready' topics that aren't yet 'Completed'."""
    status_map = get_prerequisite_status(db, user_id)
    return [t for t, status in status_map.items() if status == "Ready"]
