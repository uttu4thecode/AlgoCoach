from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import Problem, User, HintLog
from app.dependencies import get_current_user
from app.utils.groq_service import get_hint

router = APIRouter(prefix="/hints", tags=["hints"])

MAX_HINTS_PER_LEVEL = 3

class HintRequest(BaseModel):
    problem_id: int
    hint_level: int
    user_code: Optional[str] = ""

class HintResponse(BaseModel):
    hint_level: int
    hint: str
    problem_title: str
    hints_used_this_level: int
    hints_remaining: int

@router.post("/", response_model=HintResponse)
def request_hint(
    data: HintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.hint_level not in [1, 2, 3]:
        raise HTTPException(
            status_code=400,
            detail="hint_level must be 1, 2, or 3"
        )

    problem = db.query(Problem).filter(
        Problem.id == data.problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    already_used = db.query(HintLog).filter(
        HintLog.user_id == current_user.id,
        HintLog.problem_id == data.problem_id,
        HintLog.hint_level == data.hint_level
    ).count()

    if already_used >= MAX_HINTS_PER_LEVEL:
        raise HTTPException(
            status_code=429,
            detail=f"You have already used {MAX_HINTS_PER_LEVEL} hints at level {data.hint_level} for this problem. Try a different hint level or solve it yourself!"
        )

    hint_text = get_hint(
        problem_title=problem.title,
        problem_description=problem.description,
        user_code=data.user_code or "",
        hint_level=data.hint_level
    )

    log = HintLog(
        user_id=current_user.id,
        problem_id=data.problem_id,
        hint_level=data.hint_level
    )
    db.add(log)
    db.commit()

    hints_used_now = already_used + 1

    return HintResponse(
        hint_level=data.hint_level,
        hint=hint_text,
        problem_title=problem.title,
        hints_used_this_level=hints_used_now,
        hints_remaining=MAX_HINTS_PER_LEVEL - hints_used_now
    )


@router.get("/usage/{problem_id}")
def get_hint_usage(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    usage = {}
    for level in [1, 2, 3]:
        count = db.query(HintLog).filter(
            HintLog.user_id == current_user.id,
            HintLog.problem_id == problem_id,
            HintLog.hint_level == level
        ).count()
        usage[f"level_{level}"] = {
            "used": count,
            "remaining": max(0, MAX_HINTS_PER_LEVEL - count)
        }

    return {
        "problem_id": problem_id,
        "max_per_level": MAX_HINTS_PER_LEVEL,
        "usage": usage
    }