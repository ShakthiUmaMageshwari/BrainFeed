"""
Auth routes: Register and Login
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import bcrypt

from backend.db.database import get_db
from backend.db.models import User

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    department: Optional[str] = ""
    targetExams: Optional[str] = ""
    selfAssessedLevel: Optional[str] = "Beginner"
    dailyGoalQuestions: Optional[int] = 10


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    try:
        if not req.name or not req.email or not req.password:
            raise HTTPException(status_code=400, detail="Name, email, and password are required.")

        existing = db.query(User).filter(User.email == req.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered.")

        password_hash = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user_id = str(uuid.uuid4())

        user = User(
            id=user_id,
            name=req.name,
            email=req.email,
            password_hash=password_hash,
            department=req.department or "",
            target_exams=req.targetExams or "",
            self_assessed_level=req.selfAssessedLevel or "Beginner",
            daily_goal_questions=req.dailyGoalQuestions or 10,
        )
        db.add(user)
        db.commit()

        return {
            "success": True,
            "user": {
                "id": user_id,
                "name": req.name,
                "email": req.email,
                "department": req.department,
                "targetExams": req.targetExams,
                "selfAssessedLevel": req.selfAssessedLevel,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Auth] Register error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed.")


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        if not req.email or not req.password:
            raise HTTPException(status_code=400, detail="Email and password are required.")

        user = db.query(User).filter(User.email == req.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        if not bcrypt.checkpw(req.password.encode("utf-8"), user.password_hash.encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        return {
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "department": user.department,
                "targetExams": user.target_exams,
                "selfAssessedLevel": user.self_assessed_level,
                "dailyGoalQuestions": user.daily_goal_questions,
                "createdAt": user.created_at,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Auth] Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed.")
