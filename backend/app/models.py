from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.sql import func
import uuid
from app.database import Base, USING_SQLITE_FALLBACK


if USING_SQLITE_FALLBACK:
    def _uuid_col(**kwargs):
        return Column(String(36), **kwargs)

    def _uuid_default():
        return str(uuid.uuid4())

else:
    from sqlalchemy.dialects.postgresql import UUID, JSONB

    def _uuid_col(**kwargs):
        return Column(UUID(as_uuid=True), **kwargs)

    def _uuid_default():
        return uuid.uuid4()


class User(Base):
    __tablename__ = "users"

    id = _uuid_col(primary_key=True, default=_uuid_default)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student")
    college = Column(String(100))
    batch = Column(String(50))
    created_at = Column(DateTime, default=func.now())


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(10), nullable=False)
    topic = Column(String(50))
    companies = Column(JSON)
    examples = Column(JSON)
    constraints = Column(Text)
    test_cases = Column(JSON)
    created_at = Column(DateTime, default=func.now())


class Submission(Base):
    __tablename__ = "submissions"

    id = _uuid_col(primary_key=True, default=_uuid_default)
    user_id = _uuid_col(nullable=False)
    problem_id = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(30))
    status = Column(String(20))
    runtime_ms = Column(Integer)
    hints_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class HintLog(Base):
    __tablename__ = "hint_logs"

    id = _uuid_col(primary_key=True, default=_uuid_default)
    user_id = _uuid_col(nullable=False)
    problem_id = Column(Integer, nullable=False)
    hint_level = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())