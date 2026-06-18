from pydantic import BaseModel


class JobDescriptionRequest(BaseModel):
    resume_skills: list[str]
    job_description: str