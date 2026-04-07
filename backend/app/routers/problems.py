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


def _map_problem_list_rows(rows: list):
    return [ProblemListItem(**row) for row in rows]


def _map_problem_detail_row(row: dict):
    return ProblemDetail(**row)

# --- Response schema ---

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

# --- Endpoints ---

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
        return _map_problem_list_rows(rows)

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
        return _map_problem_list_rows(rows)

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
        return _map_problem_detail_row(rows[0])

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
        return _map_problem_detail_row(rows[0])



class ProblemCreate(BaseModel):
    title: str
    slug: str
    description: str
    difficulty: str
    topic: Optional[str]
    companies: Optional[List[str]]
    examples: Optional[dict]
    constraints: Optional[str]
    test_cases: Optional[dict]

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