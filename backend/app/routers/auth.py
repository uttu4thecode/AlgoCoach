from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User, Submission, Problem
from app.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    college: str = None
    batch: str = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str
    user_role: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(user_id: str, role: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        college=data.college,
        batch=data.batch
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(str(user.id), user.role, user.email)
    return TokenResponse(
        access_token=token,
        user_name=user.name,
        user_role=user.role
    )

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_token(str(user.id), user.role, user.email)
    return TokenResponse(
        access_token=token,
        user_name=user.name,
        user_role=user.role
    )


class UserResponse(BaseModel):
    name: str
    email: str
    role: str
    college: str = None
    batch: str = None

    class Config:
        from_attributes = True

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user



@router.get("/my-progress")
def my_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models import HintLog

    submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id
    ).all()

    total = len(submissions)
    accepted = len([s for s in submissions if s.status == "accepted"])

    hints_used = db.query(HintLog).filter(
        HintLog.user_id == current_user.id
    ).count()

    solved_problem_ids = {
        s.problem_id for s in submissions if s.status == "accepted"
    }

    easy_solved = medium_solved = hard_solved = 0
    topic_map = {}

    for s in submissions:
        problem = db.query(Problem).filter(Problem.id == s.problem_id).first()
        if not problem:
            continue
        topic = problem.topic
        if topic:
            if topic not in topic_map:
                topic_map[topic] = {"total": 0, "accepted": 0}
            topic_map[topic]["total"] += 1
            if s.status == "accepted":
                topic_map[topic]["accepted"] += 1

    for pid in solved_problem_ids:
        p = db.query(Problem).filter(Problem.id == pid).first()
        if p:
            if p.difficulty == "easy": easy_solved += 1
            elif p.difficulty == "medium": medium_solved += 1
            elif p.difficulty == "hard": hard_solved += 1

    # Placement Score Algorithm
    raw_score = (easy_solved * 2) + (medium_solved * 4) + (hard_solved * 7)
    accuracy = (accepted / total * 100) if total > 0 else 0
    accuracy_bonus = (accuracy / 100) * 20
    hint_penalty = min(hints_used * 0.5, 15)
    volume_bonus = min(total * 0.5, 10)
    placement_score = round(
        min(max(raw_score + accuracy_bonus + volume_bonus - hint_penalty, 0), 100), 1
    )

    if placement_score >= 80:
        level, advice = "Placement Ready", "Excellent! You are well prepared for placements."
    elif placement_score >= 60:
        level, advice = "Almost Ready", "Good progress! Focus on medium and hard problems."
    elif placement_score >= 40:
        level, advice = "In Progress", "Keep practicing. Try to solve more problems daily."
    else:
        level, advice = "Just Started", "Start with easy problems and build your confidence."

    weak_topics = [
        t for t, d in topic_map.items()
        if d["total"] > 0 and (d["accepted"] / d["total"]) < 0.5
    ]

    return {
        "placement_score": placement_score,
        "level": level,
        "advice": advice,
        "total_submissions": total,
        "accepted": accepted,
        "accuracy": round(accuracy, 2),
        "hints_used": hints_used,
        "problems_solved": len(solved_problem_ids),
        "difficulty_breakdown": {
            "easy": easy_solved,
            "medium": medium_solved,
            "hard": hard_solved
        },
        "topic_breakdown": topic_map,
        "weak_topics": weak_topics
    }