from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
import os

# Try Supabase first, fallback to SQLite if offline
try:
    if DATABASE_URL and "postgresql" in DATABASE_URL:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 5})
        # Test connection immediately
        with engine.connect() as conn:
            pass
    else:
        raise Exception("No DATABASE_URL")
except Exception as e:
    # Fallback to SQLite for local development
    print(f"[DATABASE] Supabase unavailable ({type(e).__name__}). Using SQLite locally.")
    db_path = os.path.join(os.path.dirname(__file__), "..", "algocoach.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()