from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Submission, Problem, HintLog

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _level_from_accuracy(accuracy: float) -> str:
    if accuracy >= 70:
        return "Strong"
    if accuracy >= 40:
        return "Building"
    return "Needs focus"


def _starter_code_for(slug: str) -> str:
    function_name = slug.replace("-", "_") if slug else "solve"
    return (
        "# Write your solution here\n"
        f"def {function_name}(inputs):\n"
        "    # TODO: implement\n"
        "    return None\n"
    )


def _calculate_streak(submissions: list) -> int:
    """Calculate consecutive day streak from submissions."""
    if not submissions:
        return 0

    sub_dates = {
        s.created_at.date()
        for s in submissions
        if s.created_at
    }

    streak = 0
    check_date = datetime.now(timezone.utc).date()

    while check_date in sub_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


def _calculate_placement_score(
    submissions: list,
    solved_problem_ids: set,
    hints_used: int,
    db: Session
) -> tuple[float, str, str]:
    """Calculate placement readiness score (0-100)."""
    total = len(submissions)
    accepted = len([s for s in submissions if s.status == "accepted"])

    easy_solved = medium_solved = hard_solved = 0
    for pid in solved_problem_ids:
        p = db.query(Problem).filter(Problem.id == pid).first()
        if p:
            if p.difficulty == "easy":
                easy_solved += 1
            elif p.difficulty == "medium":
                medium_solved += 1
            elif p.difficulty == "hard":
                hard_solved += 1

    raw_score = (easy_solved * 2) + (medium_solved * 4) + (hard_solved * 7)
    accuracy = (accepted / total * 100) if total > 0 else 0
    accuracy_bonus = (accuracy / 100) * 20
    hint_penalty = min(hints_used * 0.5, 15)
    volume_bonus = min(total * 0.5, 10)

    placement_score = round(
        min(max(raw_score + accuracy_bonus + volume_bonus - hint_penalty, 0), 100), 1
    )

    if placement_score >= 80:
        level = "Placement Ready"
        advice = "Excellent! You are well prepared for placements."
    elif placement_score >= 60:
        level = "Almost Ready"
        advice = "Good progress! Focus on medium and hard problems."
    elif placement_score >= 40:
        level = "In Progress"
        advice = "Keep practicing. Try to solve more problems daily."
    else:
        level = "Just Started"
        advice = "Start with easy problems and build your confidence."

    return placement_score, level, advice


@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # All submissions for this user
    submissions = db.query(Submission).filter(
        Submission.user_id == current_user.id
    ).all()

    total_submissions = len(submissions)
    accepted_submissions = len([s for s in submissions if s.status == "accepted"])
    solved_problem_ids = {
        s.problem_id for s in submissions if s.status == "accepted"
    }

    total_problems = db.query(func.count(Problem.id)).scalar() or 0
    solved_count = len(solved_problem_ids)
    accuracy = round(
        (accepted_submissions / total_submissions) * 100, 1
    ) if total_submissions else 0.0

    # Streak
    streak = _calculate_streak(submissions)

    # Hints used
    hints_used = db.query(HintLog).filter(
        HintLog.user_id == current_user.id
    ).count()

    # Placement score
    placement_score, placement_level, placement_advice = _calculate_placement_score(
        submissions, solved_problem_ids, hints_used, db
    )

    # Topic-wise focus areas
    topic_rows = (
        db.query(
            Problem.topic,
            func.count(Submission.id).label("attempts"),
            func.sum(
                case((Submission.status == "accepted", 1), else_=0)
            ).label("accepted"),
        )
        .join(Submission, Submission.problem_id == Problem.id)
        .filter(Submission.user_id == current_user.id)
        .group_by(Problem.topic)
        .order_by(func.count(Submission.id).desc())
        .limit(3)
        .all()
    )

    focus_areas = []
    for topic, attempts, accepted in topic_rows:
        topic_name = topic or "General"
        accepted_count = int(accepted or 0)
        topic_accuracy = round(
            (accepted_count / attempts) * 100, 1
        ) if attempts else 0.0
        focus_areas.append({
            "title": topic_name,
            "level": _level_from_accuracy(topic_accuracy),
            "detail": f"{accepted_count}/{attempts} accepted ({topic_accuracy}%).",
        })

    if not focus_areas:
        focus_areas = [
            {
                "title": "Arrays",
                "level": "Warm up",
                "detail": "Start with 2 easy array problems to build momentum.",
            },
            {
                "title": "Strings",
                "level": "Warm up",
                "detail": "Practice pointer-based scanning and edge cases.",
            },
            {
                "title": "Hashing",
                "level": "Warm up",
                "detail": "Use maps for frequency and lookup optimization.",
            },
        ]

    # Weak topics (less than 50% accuracy)
    weak_topics = []
    all_topic_rows = (
        db.query(
            Problem.topic,
            func.count(Submission.id).label("attempts"),
            func.sum(
                case((Submission.status == "accepted", 1), else_=0)
            ).label("accepted"),
        )
        .join(Submission, Submission.problem_id == Problem.id)
        .filter(Submission.user_id == current_user.id)
        .group_by(Problem.topic)
        .all()
    )
    for topic, attempts, accepted in all_topic_rows:
        accepted_count = int(accepted or 0)
        if attempts > 0 and (accepted_count / attempts) < 0.5:
            weak_topics.append(topic or "General")

    # Recent submissions
    recent_submissions = (
        db.query(Submission, Problem.title)
        .join(Problem, Submission.problem_id == Problem.id)
        .filter(Submission.user_id == current_user.id)
        .order_by(Submission.created_at.desc())
        .limit(5)
        .all()
    )

    recent_activity = [
        {
            "status": (submission.status or "submitted").replace("_", " ").title(),
            "title": title,
            "description": f"Language: {submission.language or 'python'}",
        }
        for submission, title in recent_submissions
    ]

    if not recent_activity:
        recent_activity = [
            {
                "status": "Ready",
                "title": "No submissions yet",
                "description": "Pick a problem and submit your first solution.",
            }
        ]

    return {
        "headline": f"Welcome back, {current_user.name}",
        "subheadline": "Keep your interview prep focused with one workspace for coding practice, review, and placement readiness.",
        "stats": [
            {
                "label": "Solved problems",
                "value": str(solved_count),
                "change": f"of {total_problems} in bank",
            },
            {
                "label": "Total submissions",
                "value": str(total_submissions),
                "change": "last 30 days",
            },
            {
                "label": "Accuracy",
                "value": f"{accuracy}%",
                "change": "accepted ratio",
            },
            {
                "label": "Current streak",
                "value": f"{streak} day{'s' if streak != 1 else ''}",
                "change": "keep consistency",
            },
        ],
        "placement": {
            "score": placement_score,
            "level": placement_level,
            "advice": placement_advice,
            "hints_used": hints_used,
            "weak_topics": weak_topics,
            "difficulty_breakdown": _get_difficulty_breakdown(
                solved_problem_ids, db
            ),
        },
        "focus_areas": focus_areas,
        "daily_plan": [
            {
                "time": "25m",
                "title": "Warm-up",
                "description": "Solve one easy problem and explain your approach out loud.",
            },
            {
                "time": "45m",
                "title": "Core practice",
                "description": "Attempt one medium problem and optimize after brute force.",
            },
            {
                "time": "20m",
                "title": "Review",
                "description": "Note mistakes, edge cases, and alternative solutions.",
            },
        ],
        "recent_activity": recent_activity,
        "roadmap": [
            {
                "phase": "Phase 1",
                "title": "Foundation",
                "description": "Master arrays, strings, and hashing patterns.",
            },
            {
                "phase": "Phase 2",
                "title": "Intermediate",
                "description": "Build speed on sliding window, stacks, and binary search.",
            },
            {
                "phase": "Phase 3",
                "title": "Advanced",
                "description": "Practice trees, graphs, and dynamic programming under time limits.",
            },
        ],
    }


def _get_difficulty_breakdown(solved_problem_ids: set, db: Session) -> dict:
    easy = medium = hard = 0
    for pid in solved_problem_ids:
        p = db.query(Problem).filter(Problem.id == pid).first()
        if p:
            if p.difficulty == "easy":
                easy += 1
            elif p.difficulty == "medium":
                medium += 1
            elif p.difficulty == "hard":
                hard += 1
    return {"easy": easy, "medium": medium, "hard": hard}


@router.get("/problems")
def get_dashboard_problems(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    del current_user
    problems = db.query(Problem).order_by(Problem.id.asc()).limit(8).all()

    return {
        "problems": [
            {
                "id": problem.id,
                "title": problem.title,
                "topic": problem.topic or "General",
                "difficulty": problem.difficulty or "Medium",
                "description": (problem.description or "").strip()[:170],
                "starterCode": _starter_code_for(problem.slug),
            }
            for problem in problems
        ]
    }