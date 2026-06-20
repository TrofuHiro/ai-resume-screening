from fastapi import FastAPI
from backend.database import engine
from backend.models import Base
from backend.routes.resume import router as resume_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(resume_router)


@app.get("/")
def root():
    return {"message": "AI Resume Screening API Running"}