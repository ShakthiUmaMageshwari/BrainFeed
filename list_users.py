
from backend.db.database import SessionLocal
from backend.db.models import User

db = SessionLocal()
users = db.query(User).all()

print(f"{'Name':<20} | {'Email':<30} | {'Password Hash (First 10 chars)'}")
print("-" * 80)
for user in users:
    print(f"{user.name:<20} | {user.email:<30} | {user.password_hash[:10]}...")

db.close()
