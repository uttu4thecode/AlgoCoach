from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, problems, submissions, hints, admin
from app.database import Base, engine
from app import models

app = FastAPI(
    title="AlgoCoach API",
    description="Smart Coding Interview Coach — Backend",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(problems.router)
app.include_router(submissions.router)
app.include_router(hints.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "AlgoCoach API is running!"}

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "AlgoCoach"}




