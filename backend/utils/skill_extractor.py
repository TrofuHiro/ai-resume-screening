import re
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
    "prisma","Figma",
    "Adobe Photoshop",
    "Adobe Illustrator",
    "Sketch"
]
def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills