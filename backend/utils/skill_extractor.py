from backend.utils.skill_mapper import normalize_skills

SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",
    "php",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "fastapi",
    "django",
    "flask",
    "laravel",
    "express",
    "react",
    "next.js",
    "docker",
    "aws",
    "git",
    "machine learning",
    "rest api",
    "prisma"
]


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    synonym_skills = normalize_skills(text)

    all_skills = list(set(found_skills + synonym_skills))

    return all_skills