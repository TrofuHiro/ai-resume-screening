from backend.utils.semantic_matcher import semantic_similarity

score = semantic_similarity(
    "docker",
    "containerization"
)

print(score)