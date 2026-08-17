"""
SQLAlchemy ORM models matching the existing brainfeed.db schema.
"""
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    elo_rating = Column(Integer, default=1200)       # Phase 2: Ranking
    learning_velocity = Column(Float, default=0.0)   # Phase 2: Metrics
    focus_score = Column(Float, default=0.0)         # Phase 2: Metrics
    department = Column(String, default="")
    target_exams = Column(String, default="")
    self_assessed_level = Column(String, default="Beginner")
    daily_goal_questions = Column(Integer, default=10)
    created_at = Column(String)


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    subtopic = Column(String, default="")
    exam_tag = Column(String, default="")
    difficulty = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON array string
    correct_answer = Column(String, nullable=False)
    explanation = Column(Text, default="")
    created_at = Column(String)


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    session_id = Column(String, nullable=True)
    selected_option = Column(String, nullable=False)
    is_correct = Column(Integer, nullable=False)
    response_time_seconds = Column(Float, nullable=False)
    hint_used = Column(Integer, default=0)
    explanation_opened = Column(Integer, default=0)
    attempt_number = Column(Integer, default=1)
    timestamp = Column(String)


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    start_time = Column(String)
    end_time = Column(String, nullable=True)
    questions_attempted = Column(Integer, default=0)
    session_duration_seconds = Column(Float, default=0)
    device_type = Column(String, default="web")


class MasteryLog(Base):
    __tablename__ = "mastery_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    mastery_score = Column(Float, nullable=False, default=0)
    level = Column(String, default="At Risk")
    updated_at = Column(String)


class QuestionStat(Base):
    __tablename__ = "question_stats"

    question_id = Column(String, ForeignKey("questions.id"), primary_key=True)
    total_attempts = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0)
    computed_difficulty = Column(String, nullable=True)
    updated_at = Column(String)


# Indexes
Index("idx_attempts_user", QuestionAttempt.user_id)
Index("idx_attempts_question", QuestionAttempt.question_id)
Index("idx_attempts_timestamp", QuestionAttempt.timestamp)
Index("idx_mastery_user_topic", MasteryLog.user_id, MasteryLog.topic)
Index("idx_sessions_user", SessionModel.user_id)


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # SCROLL, DROPOFF, EXPLANATION_VIEW, RE_ATTEMPT, HOVER
    event_data = Column(Text, nullable=True)     # JSON string for extra details
    timestamp = Column(String, nullable=False)   # ISO format


Index("idx_events_user", EventLog.user_id)
Index("idx_events_type", EventLog.event_type)
