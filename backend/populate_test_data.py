"""
Populate test account with 3+ months of realistic usage data.
Run: python backend/populate_test_data.py
"""
import sqlite3
import uuid
import random
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "brainfeed.db")
USER_ID = "95938ca0-c25e-413a-9d52-82a6a56a2cc1"

def populate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get all questions
    questions = cur.execute("SELECT id, topic, subject, difficulty FROM questions").fetchall()
    if not questions:
        print("No questions found!")
        return

    print(f"Found {len(questions)} questions")
    print(f"Populating data for user: {USER_ID}")

    # Clear existing data for this user
    cur.execute("DELETE FROM question_attempts WHERE user_id = ?", (USER_ID,))
    cur.execute("DELETE FROM sessions WHERE user_id = ?", (USER_ID,))
    cur.execute("DELETE FROM mastery_logs WHERE user_id = ?", (USER_ID,))
    conn.commit()

    now = datetime.utcnow()
    start_date = now - timedelta(days=95)  # ~3+ months ago

    # Simulate realistic learning: accuracy improves over time
    sessions_data = []
    attempts_data = []
    mastery_updates = {}

    # Generate ~60 sessions over 3 months (roughly every 1-2 days)
    session_dates = []
    current_date = start_date
    while current_date < now:
        # Some days have sessions, some don't (realistic pattern)
        if random.random() < 0.65:  # 65% chance of studying on any given day
            # Morning, afternoon, or evening session
            hour = random.choice([7, 8, 9, 10, 14, 15, 16, 19, 20, 21, 22])
            session_start = current_date.replace(hour=hour, minute=random.randint(0, 59))
            session_dates.append(session_start)
        current_date += timedelta(days=1)

    print(f"Generating {len(session_dates)} sessions over 3 months...")

    for session_idx, session_start in enumerate(session_dates):
        session_id = str(uuid.uuid4())
        duration = random.randint(300, 1800)  # 5 to 30 minutes
        session_end = session_start + timedelta(seconds=duration)
        questions_in_session = random.randint(3, 15)

        # Skill improves over time (progression curve)
        progress = session_idx / max(len(session_dates) - 1, 1)  # 0 to 1
        base_accuracy = 0.35 + progress * 0.40  # 35% → 75% over time

        sessions_data.append((
            session_id, USER_ID,
            session_start.strftime("%Y-%m-%d %H:%M:%S"),
            session_end.strftime("%Y-%m-%d %H:%M:%S"),
            questions_in_session, duration, "desktop"
        ))

        # Generate question attempts for this session
        session_questions = random.sample(questions, min(questions_in_session, len(questions)))

        for q_idx, q in enumerate(session_questions):
            q_id, topic, subject, difficulty = q

            # Adjust accuracy by difficulty
            if difficulty == "Easy":
                acc_boost = 0.15
            elif difficulty == "Hard":
                acc_boost = -0.15
            else:
                acc_boost = 0.0

            # Subject-specific strengths (simulate affinity)
            subject_boost = {"Maths": 0.10, "Aptitude": 0.05, "Reasoning": -0.05, "English": -0.10}.get(subject, 0)

            chance = min(0.95, max(0.10, base_accuracy + acc_boost + subject_boost + random.uniform(-0.15, 0.15)))
            is_correct = 1 if random.random() < chance else 0

            # Response time: faster as they improve, slower for hard questions
            base_time = 30 - progress * 15  # 30s → 15s over time
            diff_mult = {"Easy": 0.6, "Medium": 1.0, "Hard": 1.5}.get(difficulty, 1.0)
            response_time = max(3, base_time * diff_mult + random.uniform(-5, 10))

            # Some fatigue in later questions of a session
            if q_idx > 8:
                response_time *= 1.3
                if random.random() < 0.15:
                    is_correct = 0  # fatigue errors

            attempt_time = session_start + timedelta(seconds=q_idx * response_time)
            hint_used = 1 if (not is_correct and random.random() < 0.2) else 0
            explanation_opened = 1 if (not is_correct and random.random() < 0.4) else 0

            # Get attempt number
            prev_count = sum(1 for a in attempts_data if a[2] == q_id)

            attempts_data.append((
                str(uuid.uuid4()), USER_ID, q_id, session_id,
                "correct_option" if is_correct else "wrong_option",
                is_correct, round(response_time, 1),
                hint_used, explanation_opened,
                prev_count + 1,
                attempt_time.strftime("%Y-%m-%d %H:%M:%S")
            ))

            # Track mastery per topic
            if topic not in mastery_updates:
                mastery_updates[topic] = {"correct": 0, "total": 0, "times": [], "subject": subject}
            mastery_updates[topic]["correct"] += is_correct
            mastery_updates[topic]["total"] += 1
            mastery_updates[topic]["times"].append(response_time)

    # Insert sessions
    cur.executemany("""
        INSERT INTO sessions (id, user_id, start_time, end_time, questions_attempted,
                              session_duration_seconds, device_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sessions_data)
    print(f"Inserted {len(sessions_data)} sessions")

    # Insert attempts
    cur.executemany("""
        INSERT INTO question_attempts (id, user_id, question_id, session_id, selected_option,
                                       is_correct, response_time_seconds, hint_used,
                                       explanation_opened, attempt_number, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, attempts_data)
    print(f"Inserted {len(attempts_data)} question attempts")

    # Insert mastery logs
    mastery_data = []
    for topic, data in mastery_updates.items():
        accuracy = data["correct"] / data["total"] if data["total"] > 0 else 0
        avg_time = sum(data["times"]) / len(data["times"]) if data["times"] else 30
        # Mastery score: weighted combination
        speed_factor = max(0, 1 - (avg_time - 10) / 40)
        mastery_score = round(min(100, accuracy * 70 + speed_factor * 20 + min(data["total"] / 20, 1) * 10))

        # Level based on score
        if mastery_score >= 80:
            level = "Mastered"
        elif mastery_score >= 60:
            level = "Proficient"
        elif mastery_score >= 40:
            level = "Developing"
        else:
            level = "At Risk"

        mastery_data.append((
            USER_ID, topic,
            mastery_score, level,
            now.strftime("%Y-%m-%d %H:%M:%S")
        ))

    cur.executemany("""
        INSERT INTO mastery_logs (user_id, topic, mastery_score, level, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, mastery_data)
    print(f"Inserted {len(mastery_data)} mastery logs")

    # Update question_stats
    for q in questions:
        q_id = q[0]
        difficulty = q[3]
        total = sum(1 for a in attempts_data if a[2] == q_id)
        correct = sum(1 for a in attempts_data if a[2] == q_id and a[5] == 1)
        if total > 0:
            avg_time = sum(a[6] for a in attempts_data if a[2] == q_id) / total
            cur.execute("""
                INSERT OR REPLACE INTO question_stats (question_id, total_attempts, total_correct,
                    avg_response_time, computed_difficulty)
                VALUES (?, ?, ?, ?, ?)
            """, (q_id, total, correct, round(avg_time, 1), difficulty))

    conn.commit()
    conn.close()

    print("\n✅ Done! Test account populated with 3+ months of realistic data.")
    print(f"   Sessions: {len(sessions_data)}")
    print(f"   Attempts: {len(attempts_data)}")
    print(f"   Topics tracked: {len(mastery_data)}")
    print(f"   Date range: {start_date.strftime('%Y-%m-%d')} → {now.strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    populate()
