from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
import csv
import io

from app.database import get_db
from app.models import User, Submission, Problem
from app.dependencies import get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])


class StudentStats(BaseModel):
    id: str
    name: str
    email: str
    college: Optional[str]
    batch: Optional[str]
    total_submissions: int
    accepted: int
    score: float

class BatchStats(BaseModel):
    batch: str
    total_students: int
    avg_score: float
    total_submissions: int



def calculate_score(accepted: int, total: int) -> float:
    if total == 0:
        return 0.0

    volume_bonus = min(accepted * 2, 30)
    accuracy = (accepted / total) * 70
    return round(min(volume_bonus + accuracy, 100.0), 2)



@router.get("/students", response_model=List[StudentStats])
def get_all_students(
    batch: Optional[str] = None,
    college: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    query = db.query(User).filter(User.role == "student")
    if batch:
        query = query.filter(User.batch == batch)
    if college:
        query = query.filter(User.college == college)

    students = query.all()
    result = []

    for student in students:
        submissions = db.query(Submission).filter(
            Submission.user_id == student.id
        ).all()

        total = len(submissions)
        accepted = len([s for s in submissions if s.status == "accepted"])
        score = calculate_score(accepted, total)

        result.append(StudentStats(
            id=str(student.id),
            name=student.name,
            email=student.email,
            college=student.college,
            batch=student.batch,
            total_submissions=total,
            accepted=accepted,
            score=score
        ))

    result.sort(key=lambda x: x.score, reverse=True)
    return result


@router.get("/batches", response_model=List[BatchStats])
def get_batch_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    students = db.query(User).filter(User.role == "student").all()

    batch_map = {}
    for student in students:
        batch = student.batch or "Unknown"
        if batch not in batch_map:
            batch_map[batch] = {
                "students": [],
                "total_submissions": 0,
                "total_accepted": 0
            }
        batch_map[batch]["students"].append(student)

        submissions = db.query(Submission).filter(
            Submission.user_id == student.id
        ).all()

        batch_map[batch]["total_submissions"] += len(submissions)
        batch_map[batch]["total_accepted"] += len(
            [s for s in submissions if s.status == "accepted"]
        )

    result = []
    for batch_name, data in batch_map.items():
        n = len(data["students"])
        avg = calculate_score(
            data["total_accepted"],
            data["total_submissions"]
        )
        result.append(BatchStats(
            batch=batch_name,
            total_students=n,
            avg_score=avg,
            total_submissions=data["total_submissions"]
        ))

    return result


@router.get("/leaderboard", response_model=List[StudentStats])
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    students = db.query(User).filter(User.role == "student").all()
    result = []

    for student in students:
        submissions = db.query(Submission).filter(
            Submission.user_id == student.id
        ).all()
        total = len(submissions)
        accepted = len([s for s in submissions if s.status == "accepted"])
        score = calculate_score(accepted, total)

        result.append(StudentStats(
            id=str(student.id),
            name=student.name,
            email=student.email,
            college=student.college,
            batch=student.batch,
            total_submissions=total,
            accepted=accepted,
            score=score
        ))

    result.sort(key=lambda x: x.score, reverse=True)
    return result[:limit]


@router.get("/overview")
def get_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    total_students = db.query(User).filter(
        User.role == "student"
    ).count()

    total_submissions = db.query(Submission).count()

    accepted_submissions = db.query(Submission).filter(
        Submission.status == "accepted"
    ).count()

    total_problems = db.query(Problem).count()

    acceptance_rate = round(
        (accepted_submissions / total_submissions * 100)
        if total_submissions > 0 else 0, 2
    )

    return {
        "total_students": total_students,
        "total_submissions": total_submissions,
        "accepted_submissions": accepted_submissions,
        "acceptance_rate": acceptance_rate,
        "total_problems": total_problems,
    }


@router.get("/export-csv")
def export_students_csv(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    from fastapi.responses import StreamingResponse

    students = db.query(User).filter(User.role == "student").all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Name", "Email", "College", "Batch",
        "Total Submissions", "Accepted", "Score"
    ])

    for student in students:
        submissions = db.query(Submission).filter(
            Submission.user_id == student.id
        ).all()
        total = len(submissions)
        accepted = len([s for s in submissions if s.status == "accepted"])
        score = calculate_score(accepted, total)

        writer.writerow([
            student.name, student.email,
            student.college, student.batch,
            total, accepted, score
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=algocoach_students.csv"
        }
    )