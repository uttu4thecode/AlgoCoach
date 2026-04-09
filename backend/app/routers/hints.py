from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import Problem, User
from app.dependencies import get_current_user
from app.utils.groq_service import get_hint

router = APIRouter(prefix="/hints", tags=["hints"])

class HintRequest(BaseModel):
    problem_id: int
    hint_level: int        # 1, 2, or 3
    user_code: Optional[str] = ""

class HintResponse(BaseModel):
    hint_level: int
    hint: str
    problem_title: str

@router.post("/", response_model=HintResponse)
def request_hint(
    data: HintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate hint level
    if data.hint_level not in [1, 2, 3]:
        raise HTTPException(
            status_code=400,
            detail="hint_level must be 1, 2, or 3"
        )

    # Problem fetch karo
    problem = db.query(Problem).filter(
        Problem.id == data.problem_id
    ).first()

    if not problem:
        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    # Groq se hint lo
    hint_text = get_hint(
        problem_title=problem.title,
        problem_description=problem.description,
        user_code=data.user_code or "",
        hint_level=data.hint_level
    )

    return HintResponse(
        hint_level=data.hint_level,
        hint=hint_text,
        problem_title=problem.title
    )