SKILL_SYNONYMS = {
    "python": [
        "python",
        "python programming"
    ],

    "sql": [
        "sql",
        "database querying"
    ],

    "docker": [
        "docker",
        "containerization",
        "containers"
    ],

    "aws": [
        "aws",
        "amazon web services",
        "cloud infrastructure",
        "cloud computing"
    ],

    "fastapi": [
        "fastapi",
        "api development"
    ],

    "machine learning": [
        "machine learning",
        "ml",
        "artificial intelligence",
        "ai"
    ]
}


def normalize_skills(text):
    text = text.lower()
    matched = []

    for skill, synonyms in SKILL_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in text:
                matched.append(skill)
                break

    return matched