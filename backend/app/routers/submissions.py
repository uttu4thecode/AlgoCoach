from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import json

from app.database import get_db
from app.models import Problem, Submission, User
from app.dependencies import get_current_user
from app.utils.local_executor import run_code

router = APIRouter(prefix="/submissions", tags=["submissions"])

class SubmitRequest(BaseModel):
    problem_id: int
    code: str
    language: str  # python / javascript / java / cpp

class SubmissionResult(BaseModel):
    submission_id: str
    status: str
    passed: int
    total: int
    stdout: Optional[str]
    stderr: Optional[str]
    runtime: Optional[str]

@router.post("/", response_model=SubmissionResult)
async def submit_code(
    data: SubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Problem fetch karo
    problem = db.query(Problem).filter(Problem.id == data.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Test cases nikalo
    test_cases_raw = problem.test_cases or {}
    test_cases = test_cases_raw.get("test_cases", [])

    if not test_cases:
        raise HTTPException(status_code=400, detail="No test cases found for this problem")

    passed = 0
    total = len(test_cases)
    last_stdout = ""
    last_stderr = ""
    last_runtime = None

    # Har test case ke liye code run karo
    for tc in test_cases:
        stdin_data = json.dumps(tc.get("input", ""))
        expected = tc.get("expected")

        result = await run_code(data.code, data.language, stdin_data)

        last_stdout = result.get("stdout", "")
        last_stderr = result.get("stderr", "")
        last_runtime = result.get("time")

        # Simple output check
        actual_output = last_stdout.strip()
        expected_str = str(expected).strip()

        if actual_output == expected_str:
            passed += 1

    # Status decide karo
    if passed == total:
        final_status = "accepted"
    elif passed > 0:
        final_status = "partial"
    else:
        final_status = "wrong_answer"

    if last_stderr and passed == 0:
        final_status = "error"

    # DB mein save karo
    submission = Submission(
        user_id=current_user.id,
        problem_id=data.problem_id,
        code=data.code,
        language=data.language,
        status=final_status,
        runtime_ms=int(float(last_runtime) * 1000) if last_runtime else None,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return SubmissionResult(
        submission_id=str(submission.id),
        status=final_status,
        passed=passed,
        total=total,
        stdout=last_stdout,
        stderr=last_stderr,
        runtime=last_runtime,
    )

@router.get("/my", response_model=List[dict])
def my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subs = db.query(Submission).filter(
        Submission.user_id == current_user.id
    ).order_by(Submission.created_at.desc()).limit(20).all()

    return [
        {
            "id": str(s.id),
            "problem_id": s.problem_id,
            "status": s.status,
            "language": s.language,
            "runtime_ms": s.runtime_ms,
            "created_at": str(s.created_at),
        }
        for s in subs
    ]