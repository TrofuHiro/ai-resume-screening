from pydantic import BaseModel

class JobDescriptionRequest(BaseModel):
    resume_skills: list[str]
    resume_text: str
    job_description: str