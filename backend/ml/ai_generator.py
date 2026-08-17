"""
Phase 2: AI Question Generator
Generates high-quality prompts for LLMs to create educational content.
"""
from typing import Optional

def generate_question_prompt(subject: str, topic: str, difficulty: str = "Medium", exam: str = "GATE") -> str:
    """
    Generate a structured prompt for an LLM to create a new question.
    """
    return f"""
    You are an expert examiner for the {exam} exam.
    Create a {difficulty} level Multiple Choice Question (MCQ) for the subject "{subject}" and topic "{topic}".
    
    Structure your response efficiently in JSON format:
    {{
        "question_text": "The actual question text here...",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A",
        "explanation": "Detailed explanation of why A is correct and others are wrong.",
        "difficulty": "{difficulty}",
        "exam_tag": "{exam}",
        "topic": "{topic}"
    }}
    
    Guidelines:
    - {difficulty} level: {"Focus on conceptual depth and application." if difficulty == "Hard" else "Focus on core definitions and standard problems."}
    - Explanation must be educational and clear.
    - Ensure strictly valid JSON output.
    """

def generate_explanation_prompt(question_text: str, correct_answer: str, user_answer: str) -> str:
    """
    Generate a prompt to explain why a user's answer was wrong.
    """
    return f"""
    A student answered a question incorrectly.
    Question: {question_text}
    Correct Answer: {correct_answer}
    Student's Wrong Answer: {user_answer}
    
    Provide a specific, encouraging hint that explains the gap in their understanding without giving away the answer directly if they were to try again, 
    OR a full explanation if they have already failed.
    
    Keep it under 100 words.
    """
