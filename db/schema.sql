-- BrainFeed ML Database Schema

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    department TEXT,
    target_exams TEXT DEFAULT '',
    self_assessed_level TEXT DEFAULT 'Beginner',
    daily_goal_questions INTEGER DEFAULT 10,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    topic TEXT NOT NULL,
    subtopic TEXT DEFAULT '',
    exam_tag TEXT DEFAULT '',
    difficulty TEXT NOT NULL CHECK(difficulty IN ('Easy','Medium','Hard')),
    question_text TEXT NOT NULL,
    options TEXT NOT NULL, -- JSON array
    correct_answer TEXT NOT NULL,
    explanation TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS question_attempts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    question_id TEXT NOT NULL,
    session_id TEXT,
    selected_option TEXT NOT NULL,
    is_correct INTEGER NOT NULL, -- 0 or 1
    response_time_seconds REAL NOT NULL,
    hint_used INTEGER DEFAULT 0,
    explanation_opened INTEGER DEFAULT 0,
    attempt_number INTEGER DEFAULT 1,
    timestamp TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    start_time TEXT DEFAULT (datetime('now')),
    end_time TEXT,
    questions_attempted INTEGER DEFAULT 0,
    session_duration_seconds REAL DEFAULT 0,
    device_type TEXT DEFAULT 'web',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS mastery_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    mastery_score REAL NOT NULL DEFAULT 0,
    level TEXT DEFAULT 'At Risk',
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, topic)
);

CREATE TABLE IF NOT EXISTS question_stats (
    question_id TEXT PRIMARY KEY,
    total_attempts INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    avg_response_time REAL DEFAULT 0,
    computed_difficulty TEXT,
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_attempts_user ON question_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_attempts_question ON question_attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_attempts_timestamp ON question_attempts(timestamp);
CREATE INDEX IF NOT EXISTS idx_mastery_user_topic ON mastery_logs(user_id, topic);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
