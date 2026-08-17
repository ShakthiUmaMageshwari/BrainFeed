
import uuid
import bcrypt
from backend.db.database import SessionLocal
from backend.db.models import User

db = SessionLocal()

email = "test@brainfeed.com"
password = "password123"
name = "Test User"

# Check if exists
existing = db.query(User).filter(User.email == email).first()
if existing:
    print(f"User {email} already exists.")
else:
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        password_hash=password_hash,
        department="Computer Science",
        target_exams="GATE",
        self_assessed_level="Intermediate",
        daily_goal_questions=10
    )
    db.add(user)
    db.commit()
    print(f"Created user: {email} with password: {password}")

db.close()
