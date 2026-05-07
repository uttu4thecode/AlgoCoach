from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from pydantic import BaseModel
from typing import Optional, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

from app.database import get_db, USING_SQLITE_FALLBACK
from app.models import Problem
from app.dependencies import get_current_user, get_admin_user
from app.models import User
from app.config import SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/problems", tags=["problems"])


def _supabase_get(path: str, params: dict) -> list:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")

    query = urlencode(params)
    url = f"{SUPABASE_URL}/rest/v1/{path}?{query}"
    req = Request(
        url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Accept": "application/json",
        },
        method="GET",
    )
    with urlopen(req, timeout=8) as resp:
        return json.loads(resp.read().decode("utf-8"))


class ProblemListItem(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: str
    topic: Optional[str]
    companies: Optional[List[str]]

    class Config:
        from_attributes = True

class ProblemDetail(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    difficulty: str
    topic: Optional[str]
    companies: Optional[List[str]]
    examples: Optional[dict]
    constraints: Optional[str]

    class Config:
        from_attributes = True

class ProblemCreate(BaseModel):
    title: str
    slug: str
    description: str
    difficulty: str
    topic: Optional[str] = None
    companies: Optional[List[str]] = None
    examples: Optional[dict] = None
    constraints: Optional[str] = None
    test_cases: Optional[dict] = None

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    topic: Optional[str] = None
    companies: Optional[List[str]] = None
    examples: Optional[dict] = None
    constraints: Optional[str] = None
    test_cases: Optional[dict] = None


@router.get("/", response_model=List[ProblemListItem])
def get_problems(
    difficulty: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if USING_SQLITE_FALLBACK:
        params = {
            "select": "id,title,slug,difficulty,topic,companies",
            "order": "id.asc",
        }
        if difficulty:
            params["difficulty"] = f"eq.{difficulty}"
        if topic:
            params["topic"] = f"eq.{topic}"
        rows = _supabase_get("problems", params)
        return [ProblemListItem(**row) for row in rows]

    try:
        query = db.query(Problem)
        if difficulty:
            query = query.filter(Problem.difficulty == difficulty)
        if topic:
            query = query.filter(Problem.topic == topic)
        return query.all()
    except OperationalError:
        params = {
            "select": "id,title,slug,difficulty,topic,companies",
            "order": "id.asc",
        }
        if difficulty:
            params["difficulty"] = f"eq.{difficulty}"
        if topic:
            params["topic"] = f"eq.{topic}"
        rows = _supabase_get("problems", params)
        return [ProblemListItem(**row) for row in rows]


@router.get("/{slug}", response_model=ProblemDetail)
def get_problem(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if USING_SQLITE_FALLBACK:
        rows = _supabase_get(
            "problems",
            {
                "select": "id,title,slug,description,difficulty,topic,companies,examples,constraints",
                "slug": f"eq.{slug}",
                "limit": 1,
            },
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Problem not found")
        return ProblemDetail(**rows[0])

    try:
        problem = db.query(Problem).filter(Problem.slug == slug).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        return problem
    except OperationalError:
        rows = _supabase_get(
            "problems",
            {
                "select": "id,title,slug,description,difficulty,topic,companies,examples,constraints",
                "slug": f"eq.{slug}",
                "limit": 1,
            },
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Problem not found")
        return ProblemDetail(**rows[0])


@router.post("/", response_model=ProblemDetail)
def create_problem(
    data: ProblemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    existing = db.query(Problem).filter(Problem.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    problem = Problem(**data.model_dump())
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@router.put("/{problem_id}", response_model=ProblemDetail)
def update_problem(
    problem_id: int,
    data: ProblemUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(problem, field, value)

    db.commit()
    db.refresh(problem)
    return problem


@router.delete("/{problem_id}")
def delete_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    db.delete(problem)
    db.commit()
    return {"message": f"Problem '{problem.title}' deleted successfully."}