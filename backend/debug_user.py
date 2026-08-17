import sys
import os
from sqlalchemy import text
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.db.database import SessionLocal

def test_user_query():
    db = SessionLocal()
    try:
        print("Querying User table...")
        # Try to select the NEW columns
        db.execute(text("SELECT elo_rating, learning_velocity FROM users LIMIT 1"))
        print("✅ Columns exist!")
    except Exception as e:
        print(f"❌ Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_user_query()
