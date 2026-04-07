from sqlalchemy import Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student")
    college = Column(String(100))
    batch = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    
    
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(10), nullable=False)  # easy/medium/hard
    topic = Column(String(50))
    companies = Column(JSON().with_variant(ARRAY(String), "postgresql"))
    examples = Column(JSON().with_variant(JSONB, "postgresql"))
    constraints = Column(Text)
    test_cases = Column(JSON().with_variant(JSONB, "postgresql"))
    created_at = Column(DateTime, default=func.now())