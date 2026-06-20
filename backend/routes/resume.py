import os
from fastapi import APIRouter, UploadFile, File
from backend.utils.pdf_parser import extract_text_from_pdf
from backend.utils.skill_extractor import extract_skills
from backend.services.matching import calculate_match
from backend.schemas.job import JobDescriptionRequest
from backend.database import SessionLocal
from backend.models import Resume, AnalysisResult

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    extracted_text = extract_text_from_pdf(file_path)
    skills = extract_skills(extracted_text)

    db = SessionLocal()

    new_resume = Resume(
        filename=file.filename,
        raw_text=extracted_text
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    db.close()

    return {
        "resume_id": new_resume.id,
        "filename": file.filename,
        "skills": skills,
        "resume_text": extracted_text
    }

@router.post("/match")
async def match_resume(payload: JobDescriptionRequest):
    jd_skills = extract_skills(payload.job_description)

    result = calculate_match(
        payload.resume_skills,
        jd_skills,
        payload.resume_text,
        payload.job_description
    )

    db = SessionLocal()

    analysis = AnalysisResult(
        resume_id=payload.resume_id,
        score=result["score"],
        skill_score=result["skill_score"],
        semantic_score=result["semantic_score"],
        recommendation=result["recommendation"],
        matched_skills=",".join(result["matched_skills"]),
        missing_skills=",".join(result["missing_skills"])
    )

    db.add(analysis)
    db.commit()
    db.close()

    return {
        "job_skills": jd_skills,
        **result
    }

@router.get("/analysis-history")
def analysis_history():
    db = SessionLocal()

    try:
        results = (
            db.query(AnalysisResult, Resume)
            .join(Resume, AnalysisResult.resume_id == Resume.id)
            .order_by(AnalysisResult.id.desc())
            .all()
        )

        history = []

        for analysis, resume in results:
            history.append({
                "id": analysis.id,
                "resume_id": analysis.resume_id,
                "filename": resume.filename if resume else "Unknown",
                "score": analysis.score,
                "skill_score": analysis.skill_score,
                "semantic_score": analysis.semantic_score,
                "recommendation": analysis.recommendation,
                "matched_skills": analysis.matched_skills,
                "missing_skills": analysis.missing_skills
            })

        return history

    finally:
        db.close()