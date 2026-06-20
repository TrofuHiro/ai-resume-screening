from backend.utils.semantic_matcher import document_similarity


def normalize_skills(skills):
    mapping = {
        "mysql": "sql",
        "postgresql": "sql",
        "mariadb": "sql",
        "restful api": "rest api",
        "express.js": "express",
        "nextjs": "next.js"
    }

    normalized = []

    for skill in skills:
        skill = skill.lower()
        normalized.append(mapping.get(skill, skill))

    return normalized


def calculate_match(
    resume_skills,
    jd_skills,
    resume_text,
    job_description
):
    resume_skills = normalize_skills(resume_skills)
    jd_skills = normalize_skills(jd_skills)

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched = sorted(list(resume_set & jd_set))
    missing = sorted(list(jd_set - resume_set))

    if len(jd_set) == 0:
        skill_score = 0
    else:
        skill_score = (len(matched) / len(jd_set)) * 100

    semantic_score = document_similarity(
        resume_text,
        job_description
    )

    final_score = round(
        (skill_score * 0.8) + (semantic_score * 0.2),
        2
    )

    if final_score >= 80:
        recommendation = "Highly Recommended"
    elif final_score >= 60:
        recommendation = "Recommended"
    elif final_score >= 40:
        recommendation = "Consider"
    else:
        recommendation = "Not Suitable"

    return {
        "score": final_score,
        "recommendation": recommendation,
        "skill_score": round(skill_score, 2),
        "semantic_score": semantic_score,
        "matched_skills": matched,
        "missing_skills": missing
    }