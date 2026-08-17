"""
Database Verification and Repair Script.
Adds missing columns to 'users' table if they don't exist.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/brainfeed.db")

def fix_schema():
    print(f"Checking database at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found. Run the server to create it.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get existing columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Existing columns: {columns}")

        # 1. elo_rating
        if "elo_rating" not in columns:
            print("Adding 'elo_rating' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN elo_rating INTEGER DEFAULT 1200")
        else:
            print("'elo_rating' already exists.")

        # 2. learning_velocity
        if "learning_velocity" not in columns:
            print("Adding 'learning_velocity' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN learning_velocity FLOAT DEFAULT 0.0")
        else:
            print("'learning_velocity' already exists.")

        # 3. focus_score
        if "focus_score" not in columns:
            print("Adding 'focus_score' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN focus_score FLOAT DEFAULT 0.0")
        else:
            print("'focus_score' already exists.")

        conn.commit()
        print("✅ Schema repair complete.")

    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
