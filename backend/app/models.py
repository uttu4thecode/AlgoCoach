from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.sql import func
import uuid
from app.database import Base, USING_SQLITE_FALLBACK

# UUID handling — PostgreSQL vs SQLite
if USING_SQLITE_FALLBACK:
    from sqlalchemy import String as UUIDType
    def uuid_default():
        return str(uuid.uuid4())
else:
    from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
    UUIDType = UUID(as_uuid=True)
    def uuid_default():
        return uuid.uuid4()

class User(Base):
    __tablename__ = "users"

    id = Column(UUIDType if USING_SQLITE_FALLBACK else UUID(as_uuid=True), 
                primary_key=True, default=uuid_default)
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