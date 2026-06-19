import os
from fastapi import APIRouter, UploadFile, File
from backend.utils.pdf_parser import extract_text_from_pdf
from backend.utils.skill_extractor import extract_skills
from backend.services.matching import calculate_match
from backend.schemas.job import JobDescriptionRequest

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

    return {
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

    return {
        "job_skills": jd_skills,
        **result
    }