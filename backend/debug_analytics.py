"""
Debug script for Analytics Dashboard.
Calls get_dashboard directly to see if it crashes or returns invalid data.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import SessionLocal
from backend.routes.analytics import get_dashboard

def debug_dashboard():
    db = SessionLocal()
    # Use a known user ID from the logs or use a placeholder if testing logic
    # The logs showed: 95938ca0-c25e-413a-9d52-82a6a56a2cc1
    user_id = "95938ca0-c25e-413a-9d52-82a6a56a2cc1"
    
    print(f"Testing get_dashboard for user: {user_id}")
    try:
        data = get_dashboard(userId=user_id, db=db)
        print("✅ Success! Dashboard keys:")
        print(list(data.keys()))
        
        # Check specific keys causing trouble
        print(f"\nPrediction: {data.get('prediction')}")
        print(f"ExamReadiness Type: {type(data.get('examReadiness'))}")
        print(f"Mastery Type: {type(data.get('mastery'))}")
        
    except Exception as e:
        print("\n❌ CRASHED:")
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_dashboard()
