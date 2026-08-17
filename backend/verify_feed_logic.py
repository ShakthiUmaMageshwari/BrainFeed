
import requests
import uuid
import json
import time

BASE_URL = "http://localhost:8000"

def run_test():
    print("🧪 Starting Feed Logic Verification...")
    
    # 1. Register a test user
    email = f"feedtest_{uuid.uuid4().hex[:8]}@test.com"
    password = "password123"
    print(f"   Creating user: {email}")
    
    resp = requests.post(f"{BASE_URL}/api/auth/register", json={
        "name": "Feed Tester",
        "email": email,
        "password": password,
        "department": "CSE",
        "targetExams": "GATE"
    })
    
    if resp.status_code != 200:
        print(f"❌ Registration failed: {resp.text}")
        return
        
    resp_json = resp.json()
    user_id = resp_json["user"]["id"]
    print(f"   User ID: {user_id}")
    
    # 2. Consume feed multiple times
    seen_questions = set()
    
    for i in range(1, 6): # Fetch 5 batches
        print(f"\n🔄 Fetching Batch {i}...")
        resp = requests.get(f"{BASE_URL}/api/questions/feed?limit=5&userId={user_id}")
        data = resp.json()
        questions = data.get("questions", [])
        
        print(f"   Received {len(questions)} questions")
        
        batch_ids = []
        for q in questions:
            qid = q["id"]
            if qid in seen_questions:
                print(f"   ⚠️ Duplicate question found! ID: {qid}")
            batch_ids.append(qid)
            seen_questions.add(qid)
            
        # Simulate answering them to mark as "attempted"
        for qid in batch_ids:
            requests.post(f"{BASE_URL}/api/questions/submit", json={
                "userId": user_id,
                "questionId": qid,
                "selectedOption": "Option A" # Doesn't matter if correct
            })
            
    print(f"\n✅ Total unique questions served: {len(seen_questions)}")
    if len(seen_questions) == 25:
        print("✅ Infinite scroll backend logic works: Unique unattempted questions served in sequence.")
    else:
        print("❌ Logic flaw: Duplicates or missing questions.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ Test failed locally: {e}")
