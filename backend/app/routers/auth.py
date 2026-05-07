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
    submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id
    ).all()

    problem_ids = {s.problem_id for s in submissions}
    problem_topic_by_id = {}
    if problem_ids:
        problem_rows = db.query(Problem.id, Problem.topic).filter(
            Problem.id.in_(problem_ids)
        ).all()
        problem_topic_by_id = {pid: topic for pid, topic in problem_rows}

    total = len(submissions)
    accepted = len([s for s in submissions if s.status == "accepted"])
    topic_map = {}
    for s in submissions:
        topic = problem_topic_by_id.get(s.problem_id)
        if topic:
            if topic not in topic_map:
                topic_map[topic] = {"total": 0, "accepted": 0}
            topic_map[topic]["total"] += 1
            if s.status == "accepted":
                topic_map[topic]["accepted"] += 1

    return {
        "total_submissions": total,
        "accepted": accepted,
        "accuracy": round((accepted/total*100) if total > 0 else 0, 2),
        "topic_breakdown": topic_map
    }