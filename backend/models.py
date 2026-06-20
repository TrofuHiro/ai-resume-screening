from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    raw_text = Column(Text)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))

    score = Column(Float)
    skill_score = Column(Float)
    semantic_score = Column(Float)
    recommendation = Column(String)

    matched_skills = Column(Text)
    missing_skills = Column(Text)