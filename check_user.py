
from backend.db.database import SessionLocal
from backend.db.models import User

db = SessionLocal()
user = db.query(User).filter(User.email == "test@brainfeed.com").first()

if user:
    print(f"User found: {user.email}")
else:
    print("User not found")

db.close()
